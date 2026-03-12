import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
from promptpay import qrcode

from config import CURRENCY
from models.cart import cart, CartState

THEME = {
    "BG_MAIN": "#F8F9FA",        
    "BG_CARD": "#FFFFFF",        
    "TEXT_PRIMARY": "#2B2D42",   
    "TEXT_SECONDARY": "#8D99AE", 
    "ACCENT": "#FFB5A7",         
    "ACCENT_DARK": "#F28482",    
    "SUCCESS": "#84DCC6",        
    "DIVIDER": "#EDF2F4",        
    "FONT_MAIN": "Helvetica",    
}

# 🖼️ ใส่พาทไฟล์ GIF หรือ รูปภาพ ของคุณตรงนี้
PROMO_IMAGE_PATH = "nekomachines-bubble-tea-4791.gif" # เปลี่ยนเป็นชื่อไฟล์ gif ของคุณ
PROMPTPAY_PHONE_NUMBER = "0862717049" 
PROMPTPAY_DISPLAY_TEXT = "พร้อมเพย์ 086-2717049"

class CustomerScreen(tk.Toplevel):

    def __init__(self, root):
        super().__init__(root)

        self.configure(bg=THEME["BG_MAIN"])
        # self.attributes("-fullscreen", True) # เปิดใช้งานจริงเอาคอมเมนต์ออก
        self.geometry("1366x768") # ขนาดทดสอบ
        self.title("Customer Display - Minimal Cafe")

        self.main_container = tk.Frame(self, bg=THEME["BG_MAIN"])
        self.main_container.pack(fill="both", expand=True, padx=50, pady=50)

        # ==========================================
        # 🧾 LEFT PANEL: THE MINIMAL RECEIPT
        # ==========================================
        self.left_panel = tk.Frame(self.main_container, bg=THEME["BG_CARD"], highlightthickness=1, highlightbackground=THEME["DIVIDER"])
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(0, 25))

        tk.Label(self.left_panel, text="My Order", font=(THEME["FONT_MAIN"], 32, "bold"), fg=THEME["TEXT_PRIMARY"], bg=THEME["BG_CARD"], anchor="w").pack(fill="x", padx=40, pady=(40, 10))
        tk.Frame(self.left_panel, bg=THEME["DIVIDER"], height=2).pack(fill="x", padx=40, pady=(0, 20))

        self.canvas = tk.Canvas(self.left_panel, bg=THEME["BG_CARD"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.left_panel, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=THEME["BG_CARD"])

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True, padx=(40,0), pady=10)
        self.scrollbar.pack(side="right", fill="y", pady=10, padx=(0,10))

        self.total_section = tk.Frame(self.left_panel, bg=THEME["BG_CARD"], pady=30)
        self.total_section.pack(fill="x", side="bottom")
        
        tk.Frame(self.total_section, bg=THEME["DIVIDER"], height=2).pack(fill="x", padx=40, side="top", pady=(0, 20))
        tk.Label(self.total_section, text="Total", font=(THEME["FONT_MAIN"], 24, "bold"), fg=THEME["TEXT_SECONDARY"], bg=THEME["BG_CARD"]).pack(side="left", padx=40)
        self.total_lbl = tk.Label(self.total_section, text=f"0 {CURRENCY}", font=(THEME["FONT_MAIN"], 56, "bold"), fg=THEME["ACCENT_DARK"], bg=THEME["BG_CARD"])
        self.total_lbl.pack(side="right", padx=40)

        # ==========================================
        # 🧋 RIGHT PANEL: DYNAMIC CONTENT
        # ==========================================
        self.right_panel = tk.Frame(self.main_container, bg=THEME["BG_MAIN"])
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(25, 0))
        
        self.center_wrapper = tk.Frame(self.right_panel, bg=THEME["BG_MAIN"])
        self.center_wrapper.place(relx=0.5, rely=0.5, anchor="center")

        self.status_title = tk.Label(self.center_wrapper, text="Welcome!", font=(THEME["FONT_MAIN"], 56, "bold"), fg=THEME["TEXT_PRIMARY"], bg=THEME["BG_MAIN"])
        self.status_title.pack(pady=(0, 10))
        
        self.status_sub = tk.Label(self.center_wrapper, text="สั่งเครื่องดื่มที่เคาน์เตอร์ได้เลยคั้บ 🧋", font=(THEME["FONT_MAIN"], 28), fg=THEME["TEXT_SECONDARY"], bg=THEME["BG_MAIN"])
        self.status_sub.pack(pady=(0, 20))

        # 🖼️ 1. โหลดภาพ GIF และตั้งค่า Animation (แก้เรื่องภาพยืดและให้มันขยับ)
        self.promo_label = tk.Label(self.center_wrapper, bg=THEME["BG_MAIN"])
        self.gif_frames = []
        self.current_frame = 0

        try:
            img = Image.open(PROMO_IMAGE_PATH)
            # ดึงทุกเฟรมจากไฟล์ GIF
            for frame in ImageSequence.Iterator(img):
                frame_rgba = frame.convert("RGBA")
                # ใช้ thumbnail แทน resize เพื่อ "รักษาสัดส่วนเดิม" ไม่ให้ภาพยืด (กำหนดความกว้าง-ยาวสูงสุดไว้ที่ 400x400)
                frame_rgba.thumbnail((400, 400), Image.LANCZOS)
                self.gif_frames.append(ImageTk.PhotoImage(frame_rgba))
            
            if self.gif_frames:
                self.promo_label.config(image=self.gif_frames[0])
                self.animate_gif() # เรียกใช้ฟังก์ชันเล่น GIF
        except Exception as e:
            print(f"⚠️ โหลดรูป/GIF ไม่สำเร็จ: {e}")
            self.promo_label.config(
                text=f"[ โหลดรูป/GIF ไม่สำเร็จ! ]\nเช็คไฟล์: {PROMO_IMAGE_PATH}", 
                font=(THEME["FONT_MAIN"], 16), fg="red", bg="#FFE4E1", padx=20, pady=20, relief="solid", bd=1
            )

        # 📱 2. กล่อง QR Code + เบอร์พร้อมเพย์
        self.qr_frame = tk.Frame(self.center_wrapper, bg=THEME["BG_CARD"], padx=30, pady=30, highlightthickness=1, highlightbackground=THEME["DIVIDER"])
        self.qr_label = tk.Label(self.qr_frame, bg=THEME["BG_CARD"])
        self.qr_label.pack()
        
        self.pp_text_label = tk.Label(self.qr_frame, text=PROMPTPAY_DISPLAY_TEXT, font=(THEME["FONT_MAIN"], 26, "bold"), fg=THEME["ACCENT_DARK"], bg=THEME["BG_CARD"])
        self.pp_text_label.pack(pady=(15, 0))

        cart.subscribe(self.refresh)
        self.refresh()

    # ฟังก์ชันทำให้ GIF ขยับ
    def animate_gif(self):
        if self.gif_frames:
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.promo_label.config(image=self.gif_frames[self.current_frame])
            # ปรับความเร็ว GIF ได้ตรงตัวเลข 50 (มิลลิวินาที) ค่าน้อย=เร็ว, ค่ามาก=ช้า
            self.after(50, self.animate_gif)

    def show_qr(self, amount):
        payload = qrcode.generate_payload(PROMPTPAY_PHONE_NUMBER, amount)
        img = qrcode.to_image(payload).resize((400, 400))
        self.qr_img = ImageTk.PhotoImage(img)
        self.qr_label.config(image=self.qr_img)

    def refresh(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for item in cart.items:
            row_frame = tk.Frame(self.scrollable_frame, bg=THEME["BG_CARD"], pady=12)
            row_frame.pack(fill="x", padx=(0, 20))

            tk.Label(row_frame, text=item.name, font=(THEME["FONT_MAIN"], 22), fg=THEME["TEXT_PRIMARY"], bg=THEME["BG_CARD"], anchor="w").pack(side="left", fill="x", expand=True)
            tk.Label(row_frame, text=f"x{item.qty}", font=(THEME["FONT_MAIN"], 20), fg=THEME["TEXT_SECONDARY"], bg=THEME["BG_CARD"], width=4).pack(side="left", padx=10)
            tk.Label(row_frame, text=f"{item.total:,.0f}", font=(THEME["FONT_MAIN"], 24, "bold"), fg=THEME["TEXT_PRIMARY"], bg=THEME["BG_CARD"], anchor="e", width=6).pack(side="right")
            tk.Frame(self.scrollable_frame, bg=THEME["BG_MAIN"], height=1).pack(fill="x", padx=(0, 20))

        self.total_lbl.config(text=f"{cart.display_total:,.0f} {CURRENCY}")

        state = cart.state
        
        # ซ่อนทิ้งไปก่อนทั้งคู่
        self.promo_label.pack_forget()
        self.qr_frame.pack_forget()

        if state == CartState.IDLE:
            self.status_title.config(text="Welcome!", fg=THEME["ACCENT_DARK"])
            self.status_sub.config(text="สั่งเครื่องดื่มที่เคาน์เตอร์ได้เลยคั้บ 🧋", font=(THEME["FONT_MAIN"], 28))
            self.promo_label.pack(pady=20) 

        elif state == CartState.ORDERING:
            self.status_title.config(text="Your Order", fg=THEME["TEXT_PRIMARY"])
            self.status_sub.config(text="รับอะไรเพิ่มดีไหมคะ? ✨", font=(THEME["FONT_MAIN"], 28))
            self.promo_label.pack(pady=20)

        elif state == CartState.WAIT_PAYMENT:
            if cart.payment_method == "qr":
                self.status_title.config(text="Scan to Pay", fg=THEME["ACCENT_DARK"])
                self.status_sub.config(text="สแกนคิวอาร์โค้ดด้านล่างได้เลยค่ะ 👇", font=(THEME["FONT_MAIN"], 24))
                self.show_qr(cart.display_total)
                self.qr_frame.pack(pady=20) # สลับมาโชว์ QR
            else:
                self.status_title.config(text="Cash Payment", fg=THEME["TEXT_PRIMARY"])
                self.status_sub.config(text="ชำระเงินสดที่พนักงานได้เลยคั้บ 💵", font=(THEME["FONT_MAIN"], 28))
                self.promo_label.pack(pady=20)

        elif state == CartState.PAID:
            if cart.change > 0:
                self.status_title.config(text="Change", fg=THEME["TEXT_PRIMARY"])
                self.status_sub.config(text=f"เงินทอน {cart.change:,.0f} {CURRENCY}", font=(THEME["FONT_MAIN"], 64, "bold"), fg=THEME["SUCCESS"])
            else:
                self.status_title.config(text="Payment Success!", fg=THEME["SUCCESS"])
                self.status_sub.config(text="รอรับเครื่องดื่มสักครู่นะคะ 🥰", font=(THEME["FONT_MAIN"], 28))
                self.promo_label.pack(pady=20)
        
            self.after(6000, cart.reset_after_paid)