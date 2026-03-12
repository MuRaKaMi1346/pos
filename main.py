import tkinter as tk
from pathlib import Path

from config import WINDOW_WIDTH, WINDOW_HEIGHT, UI_SCALE
from database import init_db
from ui.pos_screen import POSScreen
from ui.customer_screen import CustomerScreen


# -----------------------------
# prepare environment
# -----------------------------
def prepare():
    # create folders
    Path("assets/menu").mkdir(parents=True, exist_ok=True)
    Path("data").mkdir(exist_ok=True)

    # init database
    init_db()


# -----------------------------
# multi monitor placement
# -----------------------------
def place_windows(root, customer):
    root.update_idletasks()

    # ความกว้างหน้าจอทั้งหมด
    total_width = root.winfo_screenwidth()
    height = root.winfo_screenheight()

    # ถ้ามี 2 จอ (กว้างเกิน 2000 ส่วนใหญ่ใช่)
    if total_width > 2000:
        half = total_width // 2

        # POS ซ้าย
        root.geometry(f"{half}x{height}+0+0")

        # ลูกค้า ขวา
        customer.geometry(f"{half}x{height}+{half}+0")
    else:
        # จอเดียว (โหมด dev)
        root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+50+50")
        customer.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+100+80")


# -----------------------------
# safe exit
# -----------------------------
def on_close(root):
    root.destroy()


# -----------------------------
# main app
# -----------------------------
def main():

    prepare()

    root = tk.Tk()
    root.title("Tea POS")

    # scaling สำหรับจอใหญ่
    root.tk.call('tk', 'scaling', UI_SCALE)

    # POS
    pos = POSScreen(root)

    # Customer screen
    customer = CustomerScreen(root)

    place_windows(root, customer)

    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))

    root.mainloop()


if __name__ == "__main__":
    main()
