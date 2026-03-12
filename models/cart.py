from dataclasses import dataclass
from typing import List, Callable, Optional
from enum import Enum
import random

from config import ENABLE_SMART_CENTS, SMART_CENTS_RANGE
from database import create_bill, mark_paid


# -----------------------------
# State machine
# -----------------------------
class CartState(Enum):
    IDLE = "idle"
    ORDERING = "ordering"
    WAIT_PAYMENT = "wait_payment"
    PAID = "paid"


# -----------------------------
# Item
# -----------------------------
@dataclass
class CartItem:
    name: str
    price: float
    qty: int = 1

    @property
    def total(self):
        return self.price * self.qty


# -----------------------------
# Cart Core
# -----------------------------
class Cart:

    def __init__(self):
        self.items: List[CartItem] = []
        self.state = CartState.IDLE
        self.bill_id: Optional[int] = None
        self._callbacks: List[Callable] = []
        self.payment_method = None

        self.total = 0.0
        self.display_total = 0.0   # total ที่โชว์ (รวม smart cents)
        self.change = 0.0

    # -------------------------
    # events
    # -------------------------
    def subscribe(self, fn: Callable):
        self._callbacks.append(fn)

    def _notify(self):
        for fn in self._callbacks:
            fn()

    # -------------------------
    # item ops
    # -------------------------
    def add_item(self, name: str, price: float):
        if self.state == CartState.PAID:
            return

        for item in self.items:
            if item.name == name and item.price == price:
                item.qty += 1
                break
        else:
            self.items.append(CartItem(name, price))

        self.state = CartState.ORDERING
        self._recalc()

    def remove_last(self):
        if not self.items:
            return

        item = self.items[-1]
        if item.qty > 1:
            item.qty -= 1
        else:
            self.items.pop()

        if not self.items:
            self.state = CartState.IDLE

        self._recalc()

    def cancel(self):
        self.items.clear()
        self.state = CartState.IDLE
        self.bill_id = None
        self.total = 0
        self.display_total = 0
        self._notify()

    # -------------------------
    # calc
    # -------------------------
    def _recalc(self):
        self.total = sum(i.total for i in self.items)

        # smart cents
        if ENABLE_SMART_CENTS and self.total > 0:
            cents = random.randint(*SMART_CENTS_RANGE) / 100
            self.display_total = round(self.total + cents, 2)
        else:
            self.display_total = self.total

        self._notify()

    # -------------------------
    # payment
    # -------------------------
    def begin_payment(self, method="qr"):

        if not self.items:
            return

        items_for_db = [(i.name, i.price, i.qty) for i in self.items]
        self.bill_id = create_bill(items_for_db, self.display_total)

        self.payment_method = method   # 🔥 ต้อง set ตรงนี้แน่นอน
        self.state = CartState.WAIT_PAYMENT
        self._notify()

    def pay_cash(self, money: float):

        if self.state != CartState.WAIT_PAYMENT:
            return False

        if money < self.display_total:
            return False

        self.change = round(money - self.display_total, 2)

        mark_paid(self.bill_id, "cash")

        self.state = CartState.PAID
        self._notify()        # <---- ต้องมีบรรทัดนี้หลังตั้ง change

        return True

    def confirm_transfer(self, method="qr"):
        if self.state != CartState.WAIT_PAYMENT:
            return

        self.change = 0
        mark_paid(self.bill_id, method)

        self.state = CartState.PAID
        self._notify()

    # -------------------------
    # reset after finish
    # -------------------------
    def reset_after_paid(self):
        self.items.clear()
        self.state = CartState.IDLE
        self.bill_id = None
        self.total = 0
        self.display_total = 0
        self.change = 0
        self._notify()


# global cart
cart = Cart()

print("STATE:", cart.state, "METHOD:", cart.payment_method)