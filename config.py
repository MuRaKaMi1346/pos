"""
Tea POS Configuration
แก้ค่าที่นี่ = เปลี่ยนทั้งโปรแกรม
"""

# -------------------------
# ร้านค้า
# -------------------------
SHOP_NAME = "Mhee Tea"
PROMPTPAY_PHONE = "0994523936"
CURRENCY = "บาท"

# เวลาที่แสดงหน้าขอบคุณหลังชำระเงิน (ms)
PAID_SCREEN_TIMEOUT = 4000


# -------------------------
# หน้าจอ / ขนาด
# -------------------------
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800

# auto scale สำหรับจอใหญ่ / 4K
UI_SCALE = 1.2

# ระยะห่างมาตรฐาน
PADDING = int(10 * UI_SCALE)
ROUNDNESS = 18


# -------------------------
# ธีมสี (โทนร้านชา)
# -------------------------
class Colors:
    # พื้นหลัง
    BG_MAIN = "#F6F3EE"
    BG_PANEL = "#FFFFFF"
    BG_DARK = "#2B2B2B"

    # primary (นมชา)
    PRIMARY = "#C49A6C"
    PRIMARY_DARK = "#A67C52"

    # accent (ชาเขียวมิ้น)
    ACCENT = "#4DB6AC"
    ACCENT_DARK = "#2E8B82"

    # ปุ่ม
    BTN = "#FFFFFF"
    BTN_HOVER = "#F1ECE6"

    # สถานะ
    SUCCESS = "#4CAF50"
    WARNING = "#FF9800"
    DANGER = "#E53935"
    INFO = "#2196F3"

    # ตัวอักษร
    TEXT = "#2A2A2A"
    TEXT_LIGHT = "#666666"
    TEXT_WHITE = "#FFFFFF"


# -------------------------
# ฟอนต์
# -------------------------
class Font:
    FAMILY = "Tahoma"

    def size(px):
        return int(px * UI_SCALE)

    TITLE = (FAMILY, size(32), "bold")
    HEADER = (FAMILY, size(24), "bold")
    NORMAL = (FAMILY, size(16))
    SMALL = (FAMILY, size(13))
    BIG_NUMBER = (FAMILY, size(48), "bold")


# -------------------------
# เมนู (มีหมวด + รูป)
# path รูป = assets/menu/xxx.png
# -------------------------
MENU = {
    "ชา": [
        {"name": "ชาไทย", "price": 35, "img": "thai_tea.png"},
        {"name": "ชามะนาว", "price": 30, "img": "lemon_tea.png"},
        {"name": "ชาดำ", "price": 30, "img": "ฺblack_tea.png"},
        {"name": "ชาเขียว", "price": 35, "img": "green_tea.png"},
        {"name": "มัจฉะลาเต้", "price": 45, "img": "matchalate.png"},
        {"name": "เพียวมัจฉะ", "price": 40, "img": "puremacha.png"},

    ],
    "กาแฟ": [
        {"name": "เอสเปรสโซ", "price": 40, "img": "espresso.png"},
        {"name": "ลาเต้", "price": 40, "img": "latte.png"},
        {"name": "อเมริกาโน่", "price": 40, "img": "latte.png"},
        {"name": "คาปูชิโน่", "price": 40, "img": "latte.png"},
    ],

}


# -------------------------
# การทำงาน POS
# -------------------------
# จำนวนเงินสุ่มสตางค์ (กันยอดซ้ำเวลาใช้ LINE confirm)
ENABLE_SMART_CENTS = False

# เช่น 45 -> 45.17
SMART_CENTS_RANGE = (1, 99)


# -------------------------
# Debug
# -------------------------
DEV_MODE = False
LOG_NETWORK = False