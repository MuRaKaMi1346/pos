import tkinter as tk
from config import Colors


class Numpad(tk.Toplevel):
    def __init__(self, parent, on_confirm):
        super().__init__(parent)
        self.attributes("-topmost", True)
        self.grab_set()
        self.focus()
        
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.lift()

        self.on_confirm = on_confirm
        self.value = ""

        self.title("รับเงิน")
        self.geometry("320x420")
        self.configure(bg=Colors.BG_PANEL)
        self.resizable(False, False)

        self.display = tk.Label(self, text="0",
                                font=("Kanit", 32, "bold"),
                                bg=Colors.BG_PANEL, fg="black")
        self.display.pack(pady=15)

        grid = tk.Frame(self, bg=Colors.BG_PANEL)
        grid.pack()

        buttons = [
            "7","8","9",
            "4","5","6",
            "1","2","3",
            "C","0","⌫"
        ]

        r = c = 0
        for b in buttons:
            tk.Button(grid, text=b, width=5, height=2,
                      font=("Kanit", 16, "bold"),
                      command=lambda x=b: self.press(x)
                      ).grid(row=r, column=c, padx=6, pady=6)

            c += 1
            if c == 3:
                c = 0
                r += 1

        tk.Button(self, text="✔ ยืนยัน",
                  font=("Kanit", 18, "bold"),
                  bg="#2ecc71", fg="white",
                  command=self.confirm).pack(fill="x", pady=10, padx=10)
    
        self.wait_window(self)

    def press(self, key):
        if key == "C":
            self.value = ""
        elif key == "⌫":
            self.value = self.value[:-1]
        else:
            self.value += key

        self.update_display()

    def update_display(self):
        if self.value == "":
            text = "0"
        else:
            text = self.value

        self.display.config(text=text)

        # 🔥 บังคับ Tkinter วาดทันที
        self.display.update_idletasks()

    def confirm(self):
        if self.value == "":
            return
        self.on_confirm(float(self.value))
        self.grab_release()
        self.destroy()