import tkinter as tk
from functools import partial
from datetime import datetime

from config import Colors, Font, MENU, SHOP_NAME, CURRENCY
from models.cart import cart, CartState
from database import (
    get_summary_by_date, get_bills_by_date,
    get_bill_detail, update_bill_item, recalc_bill_total,
    change_payment_method, void_bill
)
from ui.components import Panel, RoundedButton, MenuTile, BigLabel, ScrollList
from ui.numpad import Numpad


class POSScreen(tk.Frame):

    def __init__(self, root):
        super().__init__(root, bg=Colors.BG_MAIN)
        self.pack(fill="both", expand=True)

        self.current_category = list(MENU.keys())[0]

        self.left = tk.Frame(self, bg=Colors.BG_MAIN)
        self.left.pack(side="left", fill="both", expand=True)

        self.right = Panel(self)
        self.right.pack(side="right", fill="y", padx=10, pady=10)
    

        self._build_left()
        self._build_right()

        cart.subscribe(self.refresh)
        self.report_win = None
        self.refresh()

    # ---------------- MENU ----------------
    def _build_left(self):
        top = tk.Frame(self.left, bg=Colors.BG_MAIN)
        top.pack(fill="x", pady=5)

        tk.Label(top, text=SHOP_NAME, font=Font.TITLE,
                 bg=Colors.BG_MAIN, fg=Colors.TEXT).pack(side="left", padx=10)

        self.cat_frame = tk.Frame(self.left, bg=Colors.BG_MAIN)
        self.cat_frame.pack(fill="x")

        for cat in MENU.keys():
            RoundedButton(self.cat_frame, cat, Colors.PRIMARY,
                          command=partial(self.change_category, cat),
                          width=140, height=50).pack(side="left", padx=6)

        self.menu_area = tk.Frame(self.left, bg=Colors.BG_MAIN)
        self.menu_area.pack(fill="both", expand=True)

        self.render_menu()

    def change_category(self, cat):
        self.current_category = cat
        self.render_menu()

    def render_menu(self):
        for w in self.menu_area.winfo_children():
            w.destroy()

        grid = tk.Frame(self.menu_area, bg=Colors.BG_MAIN)
        grid.pack(pady=10)

        r = c = 0
        for item in MENU[self.current_category]:
            tile = MenuTile(grid,
                            item["name"],
                            item["price"],
                            item["img"],
                            command=partial(cart.add_item, item["name"], item["price"]))
            tile.grid(row=r, column=c, padx=10, pady=10)

            c += 1
            if c == 3:
                c = 0
                r += 1

    # ---------------- BILL PANEL ----------------
    def _build_right(self):
        inner = self.right.inner

        tk.Label(inner, text="รายการ", font=Font.HEADER,
                 bg=Colors.BG_PANEL, fg=Colors.TEXT).pack(pady=(10,0))

        self.listbox = ScrollList(inner)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=5)

        self.total_label = BigLabel(inner, "0")
        self.total_label.pack(pady=10)

        btns = tk.Frame(inner, bg=Colors.BG_PANEL)
        btns.pack(pady=10)

        # 🔥 ปรับความกว้างปุ่มจาก 160 เหลือ 140 จะได้ไม่ล้นกรอบ
        RoundedButton(btns, "เงินสด", Colors.SUCCESS,
                      command=self.pay_cash, width=140).grid(row=0,column=0,padx=5,pady=5)

        RoundedButton(btns, "QR", Colors.INFO,
                      command=self.pay_qr, width=140).grid(row=0,column=1,padx=5,pady=5)

        RoundedButton(btns, "ยกเลิก", Colors.DANGER,
                      command=cart.cancel, width=140).grid(row=1,column=1,padx=5,pady=5)

        # 🔥 ปรับความกว้างปุ่มยอดขายย้อนหลังให้พอดีกับปุ่มด้านบน
        RoundedButton(inner, "ยอดขายย้อนหลัง", Colors.WARNING,
                      command=self.show_report, width=300, height=50).pack(pady=10)

    def refresh(self):
        self.listbox.clear()
        for item in cart.items:
            # 🔥 ตัดชื่อเมนูถ้ายาวเกิน 18 ตัวอักษร เพื่อไม่ให้ดันตัวเลขราคาตกขอบ
            display_name = item.name if len(item.name) <= 18 else item.name[:15] + "..."
            
            # จัดฟอร์แมตให้ดูเป็นระเบียบ
            text = f"{display_name} x{item.qty}    {item.total:.2f}"
            self.listbox.add(text)
            
        self.total_label.config(text=f"{cart.display_total:.2f} {CURRENCY}")

    # ---------------- PAYMENT ----------------
    def start_payment(self):
        cart.begin_payment()

    def pay_cash(self):
        if len(cart.items) == 0:
            return

        if cart.state == CartState.ORDERING:
            cart.begin_payment("cash")

        if cart.state != CartState.WAIT_PAYMENT:
            return

        def confirm(money):
            cart.pay_cash(money)

        Numpad(self, confirm)

    def pay_qr(self):
        if len(cart.items) == 0:
            return

        if hasattr(self, "qr_win") and self.qr_win and self.qr_win.winfo_exists():
            self.qr_win.lift()
            return

        if cart.state == CartState.ORDERING:
            cart.begin_payment("qr")  

        if cart.state != CartState.WAIT_PAYMENT:
            return

        self.qr_win = tk.Toplevel(self)
        self.qr_win.title("รอเงินโอน")

        tk.Label(self.qr_win, text="รอเงินเข้าแล้วกดยืนยัน", font=Font.HEADER).pack(pady=20)

        def confirm():
            cart.confirm_transfer("qr")
            self.qr_win.destroy()

        tk.Button(self.qr_win, text="ได้รับเงินแล้ว", font=Font.NORMAL, command=confirm).pack(pady=10)

    # ---------------- REPORT ----------------
    def show_report(self):
        if self.report_win and self.report_win.winfo_exists():
            self.report_win.lift()
            return

        win = tk.Toplevel(self)
        self.report_win = win
        win.title("รายงานยอดขาย")
        win.geometry("420x600")

        top = tk.Frame(win)
        top.pack(pady=10)

        tk.Label(top, text="วันที่ (YYYY-MM-DD):").pack(side="left")

        date_entry = tk.Entry(top)
        date_entry.pack(side="left", padx=5)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        result = tk.Frame(win)
        result.pack(fill="both", expand=True)

        def load():
            for w in result.winfo_children():
                w.destroy()

            day = date_entry.get()
            s = get_summary_by_date(day)

            tk.Label(result, text=f"รวม {s['grand_total']:.2f}", font=Font.TITLE).pack(pady=10)
            tk.Label(result, text=f"เงินสด: {s['cash']:.2f}").pack()
            tk.Label(result, text=f"QR: {s['qr']:.2f}").pack()
            tk.Label(result, text="--- รายการ ---").pack(pady=5)

            for b in get_bills_by_date(day):
                bid = b["id"]
                tk.Button(result,
                          text=f"บิล #{bid}   {b['total']:.2f}   {b['payment_method']}",
                          anchor="w",
                          command=lambda bid=bid: self.open_bill_editor(bid)
                          ).pack(fill="x", padx=10, pady=2)

        tk.Button(top, text="ดู", command=load).pack(side="left", padx=5)
        load()

        win.protocol("WM_DELETE_WINDOW", lambda: [win.destroy(), setattr(self, "report_win", None)])

    # ---------------- EDIT BILL ----------------
    def open_bill_editor(self, bill_id):
        win = tk.Toplevel(self)
        win.title(f"แก้ไขบิล #{bill_id}")
        win.geometry("420x520")

        listbox = tk.Frame(win)
        listbox.pack(fill="both", expand=True, padx=10, pady=10)

        def refresh():
            for w in listbox.winfo_children():
                w.destroy()

            bill, items = get_bill_detail(bill_id)

            if hasattr(win, "total_lbl"):
                win.total_lbl.config(text=f"ยอดรวม: {bill['total']:.2f} บาท")
            else:
                win.total_lbl = tk.Label(win, text=f"ยอดรวม: {bill['total']:.2f} บาท", font=Font.HEADER)
                win.total_lbl.pack()

            for item in items:
                row = tk.Frame(listbox)
                row.pack(fill="x", pady=4)

                name = item["name"]
                qty_val = int(item["qty"])
                price = float(item["price"])
                item_id = int(item["id"])

                tk.Label(row, text=name, width=12, anchor="w").pack(side="left")

                qty = tk.IntVar(value=qty_val)

                tk.Button(row, text="-",
                    command=lambda iid=item_id, q=qty: self.change_qty(iid, int(q.get())-1, bill_id, refresh)
                ).pack(side="left")

                tk.Label(row, textvariable=qty, width=3).pack(side="left")

                tk.Button(row, text="+",
                    command=lambda iid=item_id, q=qty: self.change_qty(iid, int(q.get())+1, bill_id, refresh)
                ).pack(side="left")

                tk.Label(row, text=f"{price:.2f}").pack(side="right")

        refresh()

        tk.Button(win, text="เปลี่ยนเป็นเงินสด",
            command=lambda: self._change_payment(bill_id, "cash", refresh)
        ).pack(fill="x", padx=10, pady=2)

        tk.Button(win, text="เปลี่ยนเป็น QR",
            command=lambda: self._change_payment(bill_id, "qr", refresh)
        ).pack(fill="x", padx=10, pady=2)

        tk.Button(win, text="ยกเลิกบิล", bg="red", fg="white",
            command=lambda: self._void_bill(bill_id, win)
            ).pack(fill="x", padx=10, pady=5)

    def change_qty(self, item_id, new_qty, bill_id, refresh):
        if new_qty < 1:
            return

        update_bill_item(item_id, new_qty)
        recalc_bill_total(bill_id)

        refresh()
        self.update_idletasks()

    def _change_payment(self, bill_id, method, refresh):
        change_payment_method(bill_id, method)
        refresh()
        if self.report_win and self.report_win.winfo_exists():
            self.report_win.destroy()
            self.report_win = None
        self.show_report()

    def _void_bill(self, bill_id, win):
        void_bill(bill_id)
        win.destroy()

        if self.report_win and self.report_win.winfo_exists():
            self.report_win.destroy()
            self.report_win = None
        self.show_report()