import sqlite3
from datetime import datetime, date
from pathlib import Path
from contextlib import contextmanager
import threading

DB_PATH = Path("data")
DB_FILE = DB_PATH / "sales.db"

_lock = threading.Lock()


# ---------------------------
# Connection (สำคัญมาก)
# ---------------------------
def get_conn():
    DB_PATH.mkdir(exist_ok=True)

    # isolation_level=None = AUTO COMMIT MODE
    conn = sqlite3.connect(DB_FILE, check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def cursor():
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        try:
            yield cur
        finally:
            conn.close()


# ---------------------------
# Init / Migration
# ---------------------------
def init_db():
    with cursor() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            paid_at TEXT,
            total REAL NOT NULL,
            payment_method TEXT,
            status TEXT NOT NULL
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            qty INTEGER NOT NULL DEFAULT 1
        )
        """)

        c.execute("CREATE INDEX IF NOT EXISTS idx_bill_date ON bills(created_at)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_bill_status ON bills(status)")


# ---------------------------
# Bill Operations
# ---------------------------
def create_bill(items, total):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with cursor() as c:
        c.execute(
            "INSERT INTO bills(created_at,total,status) VALUES(?,?,?)",
            (now, total, "OPEN"),
        )
        bill_id = c.lastrowid

        for name, price, qty in items:
            c.execute(
                "INSERT INTO bill_items(bill_id,name,price,qty) VALUES(?,?,?,?)",
                (bill_id, name, price, qty),
            )

    return bill_id


def mark_paid(bill_id, method):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with cursor() as c:
        c.execute("""
            UPDATE bills
            SET paid_at=?, status='PAID', payment_method=?
            WHERE id=?
        """, (now, method, bill_id))


# ---------------------------
# Reports
# ---------------------------
def get_summary_by_date(day: str):
    with cursor() as c:
        c.execute("""
            SELECT payment_method, SUM(total) as total
            FROM bills
            WHERE status!='CANCEL' AND created_at LIKE ?
            GROUP BY payment_method
        """, (f"{day}%",))
        rows = c.fetchall()

    summary = {"cash": 0, "qr": 0, "other": 0}
    for r in rows:
        key = r["payment_method"] or "other"
        summary[key] = r["total"]

    summary["grand_total"] = sum(summary.values())
    return summary


def get_bills_by_date(day: str):
    with cursor() as c:
        c.execute("""
            SELECT id, created_at, total, payment_method
            FROM bills
            WHERE status!='CANCEL' AND created_at LIKE ?
            ORDER BY id DESC
        """, (f"{day}%",))
        return c.fetchall()


# ---------------------------
# Bill detail / edit
# ---------------------------
def get_bill_detail(bill_id):
    with cursor() as c:
        c.execute("SELECT * FROM bills WHERE id=?", (bill_id,))
        bill = c.fetchone()

        c.execute("SELECT id,name,price,qty FROM bill_items WHERE bill_id=?", (bill_id,))
        items = c.fetchall()

    return bill, items


def update_bill_item(item_id, new_qty):
    with cursor() as c:
        if new_qty <= 0:
            c.execute("DELETE FROM bill_items WHERE id=?", (item_id,))
        else:
            c.execute("UPDATE bill_items SET qty=? WHERE id=?", (new_qty, item_id))

        # 🔎 DEBUG ดูค่าหลังแก้
        c.execute("SELECT id, qty FROM bill_items WHERE id=?", (item_id,))
        print("DB NOW =", c.fetchone())


def recalc_bill_total(bill_id):
    with cursor() as c:
        c.execute("SELECT SUM(price*qty) FROM bill_items WHERE bill_id=?", (bill_id,))
        total = c.fetchone()[0] or 0

        # อัปเดตเฉพาะยอด ห้ามเปลี่ยนสถานะ
        c.execute("UPDATE bills SET total=? WHERE id=?", (total, bill_id))


def change_payment_method(bill_id, method):
    with cursor() as c:
        c.execute("UPDATE bills SET payment_method=? WHERE id=?", (method, bill_id))


def void_bill(bill_id):
    with cursor() as c:
        c.execute("UPDATE bills SET status='CANCEL' WHERE id=?", (bill_id,))