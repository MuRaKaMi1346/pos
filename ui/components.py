import tkinter as tk
from tkinter import ttk  # นำเข้า ttk เพื่อใช้ Scrollbar ที่หน้าตาทันสมัยขึ้น
from PIL import Image, ImageTk, ImageOps
from pathlib import Path


from config import Colors, Font, PADDING, ROUNDNESS

ASSET_PATH = Path("assets/menu")


# -------------------------------------------------
# helper : rounded rectangle
# -------------------------------------------------
def _round_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    points = [
        x1+r, y1,
        x2-r, y1,
        x2, y1,
        x2, y1+r,
        x2, y2-r,
        x2, y2,
        x2-r, y2,
        x1+r, y2,
        x1, y2,
        x1, y2-r,
        x1, y1+r,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


# -------------------------------------------------
# Panel
# -------------------------------------------------
class Panel(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, bg=Colors.BG_MAIN)
        self.canvas = tk.Canvas(self, bg=Colors.BG_MAIN, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg=Colors.BG_PANEL)
        self.window = self.canvas.create_window(0, 0, window=self.inner, anchor="nw")

        self.bind("<Configure>", self._resize)

    def _resize(self, e):
        self.canvas.delete("bg")
        # วาดพื้นหลัง Panel ขอบมน
        _round_rect(self.canvas, 5, 5, e.width-5, e.height-5, ROUNDNESS,
                    fill=Colors.BG_PANEL, outline="")
        self.canvas.tag_lower("bg")
        self.canvas.coords(self.window, 15, 15)  # ขยับ padding ด้านในให้โปร่งขึ้น


# -------------------------------------------------
# Rounded Button
# -------------------------------------------------
class RoundedButton(tk.Canvas):
    def __init__(self, master, text, color, command=None, width=140, height=60):
        # ใส่ cursor="hand2" ให้เป็นรูปมือเวลานำเมาส์ไปชี้
        super().__init__(master, width=width, height=height,
                         bg=Colors.BG_MAIN, highlightthickness=0, cursor="hand2")

        self.command = command
        self.color = color
        self.text = text

        self.rect = _round_rect(self, 2, 2, width-2, height-2, ROUNDNESS,
                                fill=color, outline="")

        self.label = self.create_text(width/2, height/2,
                                      text=text,
                                      font=Font.NORMAL,
                                      fill="white")

        self.bind("<Button-1>", self._click)
        self.bind("<Enter>", self._hover)
        self.bind("<Leave>", self._leave)
        
        # ผูก event ให้ text ด้วย เผื่อผู้ใช้กดโดนตัวหนังสือ
        self.tag_bind(self.label, "<Button-1>", self._click)

    def _click(self, e):
        if self.command:
            self.command()

    def _hover(self, e):
        # ให้สีจางลงหรือเปลี่ยนสีเมื่อ hover (ถ้าใน config ไม่มี PRIMARY_DARK ให้ใช้สีเทาบางๆ แทนได้)
        hover_color = getattr(Colors, "PRIMARY_DARK", "#555555") 
        self.itemconfig(self.rect, fill=hover_color)

    def _leave(self, e):
        self.itemconfig(self.rect, fill=self.color)


# -------------------------------------------------
# Big number label
# -------------------------------------------------
class BigLabel(tk.Label):
    def __init__(self, master, text="", color=Colors.TEXT):
        super().__init__(master,
                         text=text,
                         font=Font.BIG_NUMBER,
                         fg=color,
                         bg=Colors.BG_PANEL)


# -------------------------------------------------
# Menu Tile (รูป + ราคา)
# -------------------------------------------------
class MenuTile(tk.Frame):
    def __init__(self, master, name, price, img, command):
        super().__init__(master, bg=Colors.BG_MAIN)
        self.command = command

        # ใช้ highlightbackground เพื่อทำขอบกล่อง (Border) สร้างกรอบหลอกๆ
        self.box = tk.Frame(self, bg=Colors.BG_PANEL, cursor="hand2", 
                            highlightbackground=Colors.BG_MAIN, highlightthickness=2)
        self.box.pack(padx=8, pady=8, fill="both", expand=True)

        # load image
        path = ASSET_PATH / img
        if path.exists():
            # 1. เปิดรูปขึ้นมา (แปลงเป็น RGBA เผื่อรูปเป็นพื้นใส .png)
            raw_img = Image.open(path).convert("RGBA")
            
            # 2. ย่อขนาดโดยรักษาสัดส่วนเดิม (ยาวสุดไม่เกิน 100)
            # ใช้ Image.Resampling.LANCZOS เพื่อให้ภาพชัดเจนตอนย่อ (ถ้า error ให้แก้เป็น Image.LANCZOS)
            raw_img.thumbnail((100, 100), getattr(Image, 'Resampling', Image).LANCZOS)
            
            # 3. สร้างกล่องสี่เหลี่ยมจัตุรัส 100x100 สีเดียวกับพื้นหลังมารองรับ
            im = Image.new("RGBA", (100, 100), Colors.BG_PANEL)
            
            # 4. คำนวณจุดกึ่งกลางและแปะรูปลงไป (ภาพจะอยู่ตรงกลางเป๊ะและไม่ยืด)
            offset_x = (100 - raw_img.width) // 2
            offset_y = (100 - raw_img.height) // 2
            im.paste(raw_img, (offset_x, offset_y), raw_img)
            
        else:
            # รูป placeholder กรณีไม่มีรูปภาพ ให้ดูสะอาดขึ้น
            im = Image.new("RGB", (100, 100), getattr(Colors, "BG_MAIN", "#E0E0E0"))

        # 🔥 ต้องเก็บ self.image ไว้ด้วย! กันบัค Tkinter ลบรูปทิ้ง (Garbage Collection)
        self.image = im 
        self.photo = ImageTk.PhotoImage(self.image)

        tk.Label(self.box, image=self.photo, bg=Colors.BG_PANEL).pack(padx=10, pady=10)

        tk.Label(self.box, text=name, font=Font.NORMAL,
                 bg=Colors.BG_PANEL, fg=Colors.TEXT).pack()

        tk.Label(self.box, text=f"{price} ฿",
                 font=Font.SMALL, bg=Colors.BG_PANEL,
                 fg=getattr(Colors, "PRIMARY", "#00E5A8")).pack(pady=(0, 10)) # ดึงสี Primary มาเน้นราคา

        # Binding events for click and hover
        self.box.bind("<Button-1>", lambda e: self.command())
        self.box.bind("<Enter>", self._on_hover)
        self.box.bind("<Leave>", self._on_leave)
        
        for w in self.box.winfo_children():
            w.bind("<Button-1>", lambda e: self.command())
            w.bind("<Enter>", self._on_hover)
            w.bind("<Leave>", self._on_leave)

    def _on_hover(self, e):
        # เปลี่ยนสีขอบเวลานำเมาส์ไปชี้
        hover_border = getattr(Colors, "PRIMARY", "#00E5A8")
        self.box.config(highlightbackground=hover_border)

    def _on_leave(self, e):
        self.box.config(highlightbackground=Colors.BG_MAIN)


# -------------------------------------------------
# Scroll list (รายการบิล)
# -------------------------------------------------
class ScrollList(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=Colors.BG_PANEL)

        self.canvas = tk.Canvas(self, bg=Colors.BG_PANEL, highlightthickness=0)
        # เปลี่ยนมาใช้ ttk.Scrollbar ที่หน้าตาเข้ากับยุคสมัยมากกว่า
        self.scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.inner = tk.Frame(self.canvas, bg=Colors.BG_PANEL)

        self.inner.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0,0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="right", fill="y")

    def clear(self):
        for w in self.inner.winfo_children():
            w.destroy()

    def add(self, text):
        # จัด Layout รายการใหม่ เพิ่มเส้นคั่นบางๆ หรือเว้นระยะให้สวยขึ้น
        item_frame = tk.Frame(self.inner, bg=Colors.BG_PANEL)
        item_frame.pack(fill="x", padx=10, pady=2)
        
        tk.Label(item_frame, text=text,
                 font=Font.NORMAL,
                 anchor="w",
                 bg=Colors.BG_PANEL,
                 fg=Colors.TEXT).pack(side="left", fill="x", expand=True, pady=6)
        
        # เพิ่มเส้นคั่นระหว่างรายการ (Separator)
        tk.Frame(self.inner, bg=getattr(Colors, "BG_MAIN", "#CCCCCC"), height=1).pack(fill="x", padx=10)