import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

from config import Config
from predict import FearClassifier

def _round_rect(canvas, x1, y1, x2, y2, r=20, **kwargs):
    points = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class App(tk.Tk):
    W, H = 960, 540

    def __init__(self):
        super().__init__()
        self.title("Аналіз апеляції до страху")
        self.geometry(f"{self.W}x{self.H}")
        self.resizable(False, False)

        try:
            self.clf = FearClassifier(str(Config.MODEL_DIR), max_length=Config.MAX_LENGTH)
        except Exception as e:
            messagebox.showerror("Помилка моделі", f"Не вдалося завантажити модель:\n{e}")
            self.destroy()
            return

        self.threshold_var = tk.DoubleVar(value=Config.THRESHOLD)
        self._build_ui()
        self._setup_bindings()
        self._create_context_menu()

    def _build_ui(self):
        self.canvas = tk.Canvas(self, width=self.W, height=self.H, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # 1. Завантаження фону
        bg_path = os.path.join(os.path.dirname(__file__), "..", "assets", "ui_bg.png")
        try:
            img = Image.open(bg_path).resize((self.W, self.H), Image.LANCZOS)
            self.bg_img = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        except:
            self.canvas.config(bg="#E2E8F0")

        color_blue = "#8DAFCB"
        color_pink = "#F1919A"

        tx, ty, tw, th = 130, 130, 700, 180
        _round_rect(self.canvas, tx, ty, tx + tw, ty + th, r=20, fill="#FFFFFF", outline=color_blue, width=2)

        self.txt = tk.Text(
            self, wrap="word", undo=True, font=("Segoe UI", 12),
            bd=0, padx=5, pady=5, highlightthickness=0, bg="#FFFFFF"
        )
        self.txt.place(x=tx + 15, y=ty + 15, width=tw - 30, height=th - 30)
        self.txt.insert("1.0", "Вставте текст для аналізу тут...")
        self.txt.bind("<FocusIn>", self._clear_placeholder)

        rx, ry, rw, rh = 130, 330, 430, 150
        _round_rect(self.canvas, rx, ry, rx + rw, ry + rh, r=20, fill=color_blue, outline="")

        self.result_lbl = tk.Label(
            self, text="Очікування аналізу...", font=("Segoe UI", 16, "bold"),
            bg=color_blue, fg="#FFFFFF"
        )
        self.result_lbl.place(x=rx + 25, y=ry + 15)

        self.details_lbl = tk.Label(
            self, text="Ймовірності:\nСтрах: - | Нейтрально: -", font=("Segoe UI", 12),
            bg=color_blue, fg="#FFFFFF", justify="left"
        )
        self.details_lbl.place(x=rx + 25, y=ry + 60)

        cx, cy, cw, ch = 580, 330, 250, 150
        _round_rect(self.canvas, cx, cy, cx + cw, cy + ch, r=20, fill=color_pink, outline="")

        tk.Label(
            self, text="Поріг чутливості:", font=("Segoe UI", 10, "bold"), bg=color_pink, fg="#FFFFFF"
        ).place(x=cx + 20, y=cy + 25)

        entry_bg = tk.Frame(self, bg="#FFFFFF", padx=1, pady=1)
        entry_bg.place(x=cx + 155, y=cy + 25, width=45, height=24)
        
        self.thr_entry = tk.Entry(
            entry_bg, textvariable=self.threshold_var, font=("Segoe UI", 11),
            bd=0, justify="center", bg="#FFFFFF"
        )
        self.thr_entry.pack(fill="both", expand=True)

        # Кнопки зроблені трохи ширшими
        self._create_canvas_button(cx + 15, cy + 80, 105, 40, "АНАЛІЗ", "#FFFFFF", "#D85C66", self.on_predict)
        self._create_canvas_button(cx + 130, cy + 80, 105, 40, "ОЧИСТИТИ", "#FFFFFF", "#888888", self.on_clear)

    def _create_canvas_button(self, x, y, w, h, text, bg_color, fg_color, command):
        rect_id = _round_rect(self.canvas, x, y, x + w, y + h, r=12, fill=bg_color)
        text_id = self.canvas.create_text(
            x + w/2, y + h/2, text=text, fill=fg_color, font=("Segoe UI", 10, "bold")
        )
        
        hover_color = "#F0F0F0"
        
        def on_enter(e): self.canvas.itemconfig(rect_id, fill=hover_color)
        def on_leave(e): self.canvas.itemconfig(rect_id, fill=bg_color)
        def on_click(e): command()

        for item in (rect_id, text_id):
            self.canvas.tag_bind(item, "<Enter>", on_enter)
            self.canvas.tag_bind(item, "<Leave>", on_leave)
            self.canvas.tag_bind(item, "<Button-1>", on_click)

    def _create_context_menu(self):
        self.menu = tk.Menu(self, tearoff=0, font=("Segoe UI", 10))
        self.menu.add_command(label="Копіювати", command=self._copy_text)
        self.menu.add_command(label="Вставити", command=self._paste_text)
        self.menu.add_command(label="Вирізати", command=self._cut_text)
        
        self.txt.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def _setup_bindings(self):
        self.bind("<Control-v>", self._paste_text)
        self.bind("<Control-V>", self._paste_text)
        self.bind("<Control-c>", self._copy_text)
        self.bind("<Control-C>", self._copy_text)
        self.bind("<Control-x>", self._cut_text)
        self.bind("<Control-X>", self._cut_text)

    def _copy_text(self, event=None):
        try:
            text = self.txt.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)
        except tk.TclError:
            pass
        return "break"

    def _cut_text(self, event=None):
        self._copy_text()
        try:
            self.txt.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass
        return "break"

    def _paste_text(self, event=None):
        try:
            text_to_paste = self.clipboard_get()
            try:
                self.txt.delete(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                pass
            self.txt.insert(tk.INSERT, text_to_paste)
        except tk.TclError:
            pass
        return "break"

    def _clear_placeholder(self, event):
        if "Вставте текст для аналізу тут" in self.txt.get("1.0", "end-1c"):
            self.txt.delete("1.0", "end")

    def on_clear(self):
        self.txt.delete("1.0", "end")
        self.txt.insert("1.0", "Вставте текст для аналізу тут...")
        self.result_lbl.config(text="Очікування аналізу...", fg="#FFFFFF")
        self.details_lbl.config(text="Ймовірності:\nСтрах: - | Нейтрально: -")
        self.focus()

    def on_predict(self):
        text = self.txt.get("1.0", "end").strip()
        if not text or "Вставте текст для аналізу тут" in text:
            messagebox.showwarning("Текст відсутній", "Будь ласка, введіть або вставте текст.")
            return

        try:
            threshold = float(self.threshold_var.get())
            res = self.clf.predict(text, threshold=threshold)
            
            p_fear = res['p1'] * 100
            p_neutral = res['p0'] * 100

            if res["label"] == 1:
                self.result_lbl.config(text="ВИЯВЛЕНО СТРАХ", fg="#4A0000") 
            else:
                self.result_lbl.config(text="СТРАХУ НЕМАЄ", fg="#004A14")
            
            self.details_lbl.config(
                text=f"Ймовірності (Поріг: {threshold:.2f})\nАпеляція до страху: {p_fear:.1f}%\nНейтральний текст: {p_neutral:.1f}%"
            )
        except ValueError:
            messagebox.showerror("Помилка", "Будь ласка, введіть коректне числове значення для порогу (наприклад, 0.55).")
        except Exception as e:
            messagebox.showerror("Помилка", f"Виникла помилка під час аналізу:\n{e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()