# language: Python, file: aura.py
# AURA Prank: визуальный пранк. Не удаляет и не шифрует данные.
# Запускать только в виртуальной машине.

import os
import sys
import random
import ctypes
import threading
import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

APP_NAME = "AURA"
APPDATA = os.environ.get("APPDATA", ".")
BASE_DIR = os.path.join(APPDATA, "AURA_Prank")
DESKTOP_FILES_DIR = os.path.join(BASE_DIR, "files")

MESSAGES = [
    "AURA +10000", "AURA +100000000000", "AURA +999999999999",
    "МАКСИМАЛЬНЫЙ AURA", "AURA ЗАГРУЖЕН", "ТЫ ПОЛУЧИЛ AURA",
    "AURA +50000", "AURA +777777777", "AURA OVERFLOW",
    "AURA +1000000", "AURA АКТИВИРОВАН", "AURA +123456789",
]

WALLPAPER_REL = "assets/wallpaper.png"
SOUND_REL = "assets/sound.mp3"
PHOTO_DIR_REL = "assets/photos"

def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)

def get_desktop_path():
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
        val, _ = winreg.QueryValueEx(key, "Desktop")
        winreg.CloseKey(key)
        return os.path.expandvars(val)
    except Exception:
        return os.path.join(os.environ.get("USERPROFILE", "."), "Desktop")

def set_wallpaper(path):
    try:
        SPI_SETDESKWALLPAPER = 0x0014
        SPIF_UPDATEINIFILE = 0x01
        SPIF_SENDCHANGE = 0x02
        ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER, 0, path,
            SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
        )
    except Exception as e:
        print(f"[!] Wallpaper error: {e}")

def play_sound(path):
    if not HAS_PYGAME:
        print("[!] pygame not found, sound disabled")
        return
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"[!] Sound error: {e}")

def create_aura_files(count=300):
    desktop = get_desktop_path()
    os.makedirs(DESKTOP_FILES_DIR, exist_ok=True)
    for i in range(count):
        name = f"AURA_{i:04d}.txt"
        dst = os.path.join(desktop, name)
        if os.path.exists(dst):
            continue
        try:
            with open(dst, "w", encoding="utf-8") as f:
                f.write(f"AURA +{random.randint(1000, 999999999)}\n")
        except Exception:
            pass

def overlay(root, photo_paths):
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()

    top = tk.Toplevel(root)
    top.overrideredirect(True)
    top.geometry(f"{sw}x{sh}+0+0")
    top.attributes("-topmost", True)
    top.attributes("-transparentcolor", "magenta")
    top.configure(bg="magenta")
    top.protocol("WM_DELETE_WINDOW", lambda: None)

    canvas = tk.Canvas(top, width=sw, height=sh, bg="magenta", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Фикс: привязываем клики к оверлею, чтобы они не проходили на рабочий стол
    canvas.create_rectangle(0, 0, 1, 1, fill="black", outline="")

    imgs = []
    for p in photo_paths:
        try:
            im = Image.open(p).convert("RGBA").resize((48, 48))
            imgs.append(ImageTk.PhotoImage(im))
        except Exception:
            pass

    if not imgs:
        print("[!] No photos found, overlay will be empty")
        return

    items = []
    for _ in range(800):
        ph = random.choice(imgs)
        x = random.randint(0, max(1, sw - 48))
        y = random.randint(0, max(1, sh - 48))
        item = canvas.create_image(x, y, image=ph, anchor="nw")
        items.append((item, ph))

    def spawn_loop():
        if len(items) >= 2000:
            return
        for _ in range(3):
            if len(items) >= 2000:
                break
            ph = random.choice(imgs)
            x = random.randint(0, max(1, sw - 48))
            y = random.randint(0, max(1, sh - 48))
            item = canvas.create_image(x, y, image=ph, anchor="nw")
            items.append((item, ph))
        top.after(200, spawn_loop)

    top.after(100, spawn_loop)

def message_loop(root):
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()

    def spawn():
        try:
            win = tk.Toplevel(root)
            win.overrideredirect(True)
            win.attributes("-topmost", True)
            win.configure(bg="black")
            text = random.choice(MESSAGES)
            f = font.Font(family="Arial", size=random.randint(18, 40), weight="bold")
            lbl = tk.Label(win, text=text, fg="#00FF00", bg="black", font=f)
            lbl.pack(padx=10, pady=5)
            x = random.randint(0, max(1, sw - 300))
            y = random.randint(0, max(1, sh - 100))
            win.geometry(f"+{x}+{y}")
            win.after(random.randint(1500, 4000), win.destroy)
        except Exception:
            pass
        root.after(random.randint(100, 400), spawn)

    root.after(500, spawn)

def main():
    schedule_wallpaper_thread = threading.Thread(target=set_wallpaper, args=(resource_path(WALLPAPER_REL),), daemon=True)
    schedule_wallpaper_thread.start()

    snd = resource_path(SOUND_REL)
    if os.path.exists(snd):
        threading.Thread(target=play_sound, args=(snd,), daemon=True).start()

    threading.Thread(target=create_aura_files, args=(300,), daemon=True).start()

    photo_dir = resource_path(PHOTO_DIR_REL)
    photo_paths = []
    if os.path.isdir(photo_dir):
        for name in os.listdir(photo_dir):
            if name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                photo_paths.append(os.path.join(photo_dir, name))

    root = tk.Tk()
    root.withdraw()
    root.title("AURA")
    root.protocol("WM_DELETE_WINDOW", lambda: None)
    root.geometry("1x1+0+0")

    overlay(root, photo_paths)
    message_loop(root)

    root.mainloop()

if __name__ == "__main__":
    main()
