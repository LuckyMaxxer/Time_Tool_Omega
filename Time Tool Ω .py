import json
import os
import re
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta


DARK = "#1e1e1e"
PANEL = "#252526"
PANEL2 = "#2d2d30"
FG = "#e0e0e0"
MUTED = "#8a8a8a"
SUBTLE = "#9e9e9e"
BR = "#3f3f46"
ENTRY_BG = "#3a3a3f"
GREEN = "#81c784"
RED = "#ef5350"
BLUE = "#64b5f6"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRIENDS_FILE = os.path.join(BASE_DIR, "friends.txt")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return None
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
        geom = data.get("geometry")
        if not isinstance(geom, str):
            return None
        m = re.match(r"^(\d+)x(\d+)([+-]\d+)([+-]\d+)$", geom)
        if not m:
            return None
        w, h = int(m.group(1)), int(m.group(2))
        if w < 400 or h < 300:
            return None
        return geom
    except (OSError, ValueError):
        return None


def save_settings(root):
    try:
        w, h = root.winfo_width(), root.winfo_height()
        if w > 0 and h > 0:
            x, y = root.winfo_x(), root.winfo_y()
            data = {"geometry": f"{w}x{h}+{x}+{y}"}
            with open(SETTINGS_FILE, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
    except (OSError, tk.TclError):
        pass


def apply_dark_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", background=DARK, foreground=FG, fieldbackground=ENTRY_BG, bordercolor=BR)
    style.configure("TFrame", background=DARK)
    style.configure("TLabel", background=DARK, foreground=FG)
    style.configure("TButton", background=PANEL2, foreground=FG, bordercolor=BR, padding=(8, 4))
    style.map("TButton", background=[("active", "#3f3f46")], foreground=[("disabled", MUTED)])
    style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=FG, insertcolor=FG,
                    bordercolor=BR, lightcolor=BR, darkcolor=BR)
    style.map("TEntry", fieldbackground=[("readonly", ENTRY_BG)])
    style.configure("TNotebook", background=DARK, borderwidth=0)
    style.configure("TNotebook.Tab", background=PANEL2, foreground="#b0b0b0", padding=(12, 6), borderwidth=1)
    style.map("TNotebook.Tab", background=[("selected", BLUE)], foreground=[("selected", "#0b0b0b")])
    style.configure("TSeparator", background=BR)
    style.configure("Friend.TFrame", background=PANEL, relief="flat", borderwidth=1)
    style.configure("Title.TLabel", background=DARK, foreground=FG, font=("Segoe UI", 12, "bold"))
    style.configure("Head.TLabel", background=DARK, foreground=FG, font=("Segoe UI", 11, "bold"))
    root.configure(bg=DARK)
    return enable_dark_title_bar(root)


def enable_dark_title_bar(root):
    try:
        import ctypes
        hwnd = ctypes.windll.user32.GetAncestor(root.winfo_id(), 2)  # GA_ROOT
        ctypes.windll.uxtheme.SetWindowTheme(hwnd, "DarkMode_Explorer", None)
        value = ctypes.c_int(1)
        dwm = ctypes.windll.dwmapi
        ok = False
        for attr in (20, 19):  # DWMWA_USE_IMMERSIVE_DARK_MODE
            if dwm.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(value), ctypes.sizeof(value)) == 0:
                ok = True
                break
        return ok
    except Exception:
        return False


def parse_time(text):
    text = text.strip().lower()
    m = re.match(r"^(\d{1,2})(?::)?(\d{2})?\s*(am|a\.m\.|pm|p\.m\.)?$", text)
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2)) if m.group(2) else 0
    ampm = m.group(3)
    if minute > 59:
        return None
    if ampm:
        ap = ampm[0]
        if hour > 12 or hour < 1:
            return None
        if ap == "a":
            hour = 0 if hour == 12 else hour
        else:
            hour = 12 if hour == 12 else hour + 12
    else:
        if hour > 23:
            return None
    return (hour, minute, ampm is not None)


def convert_to_12(hour, minute):
    ampm = "AM"
    h = hour % 24
    if h >= 12:
        ampm = "PM"
    h12 = h % 12 or 12
    return f"{h12}:{minute:02d} {ampm}"


def normalize_offset(minutes):
    while minutes > 720:
        minutes -= 1440
    while minutes <= -720:
        minutes += 1440
    return minutes


def format_offset(minutes):
    sign = "+" if minutes >= 0 else "-"
    abs_min = abs(minutes)
    return f"{sign}{abs_min // 60:02d}:{abs_min % 60:02d}"


def parse_offset(text):
    text = text.strip().replace(" ", "")
    m = re.match(r"^([+-])?(\d{1,3})(?::(\d{2}))?$", text)
    if not m:
        return None
    sign = -1 if m.group(1) == "-" else 1
    hour = int(m.group(2))
    minute = int(m.group(3) or 0)
    if minute > 59:
        return None
    return normalize_offset(sign * (hour * 60 + minute))


def day_hint(my_date, friend_date):
    return friend_date.strftime("%a %d")


class PEntry(tk.Entry):
    PH_COLOR = "#686872"

    def __init__(self, master, placeholder, **kw):
        kw.setdefault("relief", "flat")
        kw.setdefault("highlightthickness", 1)
        kw.setdefault("highlightbackground", BR)
        kw.setdefault("highlightcolor", BR)
        kw.setdefault("insertbackground", FG)
        kw.setdefault("bg", ENTRY_BG)
        kw.setdefault("fg", FG)
        kw.setdefault("selectbackground", BLUE)
        kw.setdefault("selectforeground", "#0b0b0b")
        self._var = tk.StringVar()
        kw["textvariable"] = self._var
        super().__init__(master, **kw)
        self.ph = placeholder
        self.ph_label = tk.Label(
            self, text=placeholder, fg=self.PH_COLOR, bg=ENTRY_BG,
            font=self.cget("font"), anchor="w", bd=0, highlightthickness=0, padx=0, pady=0,
        )
        self.ph_label.bind("<Button-1>", lambda e: self.focus_set())
        self._var.trace_add("write", self._sync)
        self._sync()

    def _sync(self, *a):
        if self.get():
            self.ph_label.place_forget()
        else:
            self.ph_label.place(relx=0.0, x=3, rely=0.5, anchor="w")


def load_friends():
    data = []
    if os.path.exists(FRIENDS_FILE):
        with open(FRIENDS_FILE, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "," not in line:
                    continue
                name, off = line.split(",", 1)
                try:
                    data.append((name.strip(), int(off.strip())))
                except ValueError:
                    continue
    return data


def save_friends(friends):
    with open(FRIENDS_FILE, "w", encoding="utf-8") as fh:
        fh.write("# Time Tool friends: name,offset_in_minutes\n")
        for row in friends:
            fh.write(f"{row.name},{row.offset}\n")


class ConverterTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=16)
        self._build()
        self._convert()

    def _build(self):
        self.columnconfigure(0, weight=1)
        ttk.Label(self, text="Enter a time in either format:").grid(row=0, column=0, sticky="w")

        self.entry = PEntry(self, "15:45 or 3:45 PM", width=24, font=("Consolas", 16))
        self.entry.grid(row=1, column=0, sticky="we", pady=(8, 4))
        self.entry.bind("<KeyRelease>", lambda e: self._convert())
        self.entry.focus_set()

        self.result = ttk.Label(self, text="", font=("Consolas", 18))
        self.result.grid(row=2, column=0, sticky="w", pady=(8, 4))

    def _convert(self, event=None):
        text = self.entry.get().strip()
        if not text:
            return
        parsed = parse_time(text)
        if parsed is None:
            self.result.config(text="(invalid format)", foreground=RED)
            return
        hour, minute, is_ampm = parsed
        if is_ampm:
            self.result.config(text=f"{hour:02d}:{minute:02d}", foreground=GREEN)
        else:
            self.result.config(text=convert_to_12(hour, minute), foreground=GREEN)


class TimeDiffTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=16)
        self.last_offset_min = None
        self._build()
        self._calculate()

    def _build(self):
        self.columnconfigure(0, weight=1)
        ttk.Label(self, text="When it's this time for YOU:").grid(row=0, column=0, sticky="w")
        self.my_entry = PEntry(self, "e.g. 15:00", width=16, font=("Consolas", 14))
        self.my_entry.grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.my_entry.bind("<Return>", lambda e: self.f_entry.focus_set())

        ttk.Label(self, text="...what time is it for your FRIEND?", foreground="#c8c8c8").grid(
            row=2, column=0, sticky="w", pady=(12, 0)
        )
        self.f_entry = PEntry(self, "e.g. 5:00 AM", width=16, font=("Consolas", 14))
        self.f_entry.grid(row=3, column=0, sticky="w", pady=(4, 0))
        self.f_entry.bind("<Return>", lambda e: self._calculate())

        ttk.Button(self, text="Calculate difference", command=self._calculate).grid(
            row=4, column=0, sticky="w", pady=(12, 8)
        )

        self.result = ttk.Label(self, text="", font=("Segoe UI", 13))
        self.result.grid(row=5, column=0, sticky="w")
        self.off_lbl = ttk.Label(self, text="", font=("Consolas", 16, "bold"))
        self.off_lbl.grid(row=6, column=0, sticky="w", pady=(6, 0))

    def _calculate(self):
        a_raw = self.my_entry.get()
        b_raw = self.f_entry.get()
        a = None if not a_raw.strip() else parse_time(a_raw)
        b = None if not b_raw.strip() else parse_time(b_raw)
        if a is None and b is None:
            self.last_offset_min = None
            self.result.config(text="")
            self.off_lbl.config(text="")
            return
        if a is None or b is None:
            self.last_offset_min = None
            self.result.config(text="Enter both times (e.g. 15:00, 5:00 AM).", foreground=RED)
            self.off_lbl.config(text="")
            return
        diff = normalize_offset((b[0] * 60 + b[1]) - (a[0] * 60 + a[1]))
        self.last_offset_min = diff

        if diff == 0:
            self.result.config(text="Same time for both of you.", foreground=GREEN)
            self.off_lbl.config(text="\u00b100:00", foreground=GREEN)
            return

        h = abs(diff) // 60
        m = abs(diff) % 60
        if diff > 0:
            sentence = f"Friend is {h}:{m:02d} ahead of you."
            color = GREEN
        else:
            sentence = f"Friend is {h}:{m:02d} behind you."
            color = RED
        self.result.config(text=sentence, foreground=color)
        self.off_lbl.config(text=f"offset {format_offset(diff)}", foreground=color)


class ClockRow(ttk.Frame):
    def __init__(self, master, name, offset_min, on_remove=None):
        super().__init__(master, padding=(8, 4), style="Friend.TFrame")
        self.name = name
        self.offset = offset_min
        self.columnconfigure(1, weight=1)

        self.name_lbl = ttk.Label(self, text=name, font=("Segoe UI", 11, "bold"), width=16, anchor="w")
        self.name_lbl.grid(row=0, column=0, sticky="w")
        self.off_lbl = ttk.Label(self, text=format_offset(offset_min), font=("Consolas", 11), foreground=BLUE)
        self.off_lbl.grid(row=1, column=0, sticky="w")
        self.day_lbl = ttk.Label(self, text="", font=("Segoe UI", 9), foreground=MUTED)
        self.day_lbl.grid(row=0, column=2, sticky="e", padx=(8, 4))
        self.time_lbl = ttk.Label(self, text="", font=("Consolas", 16))
        self.time_lbl.grid(row=1, column=2, sticky="e", padx=(8, 4))
        if on_remove is not None:
            ttk.Button(self, text="\u2715", width=3, command=lambda: on_remove(self)).grid(
                row=0, column=3, rowspan=2, sticky="e"
            )

    def tick(self, my_now):
        friend_wall = my_now + timedelta(minutes=self.offset)
        self.time_lbl.config(text=friend_wall.strftime("%H:%M:%S"))
        self.day_lbl.config(text=day_hint(my_now.date(), friend_wall.date()))


class ClocksTab(ttk.Frame):
    def __init__(self, master, diff_tab):
        super().__init__(master, padding=16)
        self.diff_tab = diff_tab
        self.friends = []
        self._build()
        for name, offset in load_friends():
            self._add_friend_named(name, offset)
        self._tick()

    def _build(self):
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Local Time", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        self.my_time_lbl = ttk.Label(self, text="", font=("Consolas", 26))
        self.my_time_lbl.grid(row=1, column=0, sticky="w", pady=(2, 8))

        ttk.Separator(self, orient="horizontal").grid(row=2, column=0, sticky="we", pady=6)

        self.friends_frame = ttk.Frame(self)
        self.friends_frame.grid(row=3, column=0, sticky="we")
        self.friends_frame.columnconfigure(0, weight=1)

        ttk.Separator(self, orient="horizontal").grid(row=4, column=0, sticky="we", pady=6)

        add = ttk.Frame(self)
        add.grid(row=5, column=0, sticky="we", pady=(4, 0))
        add.columnconfigure(1, weight=1)
        self.name_entry = PEntry(add, "name", width=16)
        self.name_entry.grid(row=0, column=0, padx=(0, 6))
        self.offset_entry = PEntry(add, "offset", width=9)
        self.offset_entry.grid(row=0, column=1, sticky="we")
        ttk.Button(add, text="Add friend", command=self._add_friend).grid(row=0, column=2, padx=(6, 6))
        ttk.Button(add, text="Use computed offset", command=self._use_computed).grid(row=0, column=3)

        self.empty_lbl = ttk.Label(self, text="No friends yet \u2014 add one above.", foreground=MUTED)
        self.empty_lbl.grid(row=3, column=0, sticky="w", padx=12, pady=8)

    def _add_friend(self):
        name = self.name_entry.get().strip() or "Friend"
        off_raw = self.offset_entry.get()
        if not off_raw.strip():
            return
        offset = parse_offset(off_raw)
        if offset is None:
            return
        self._add_friend_named(name, offset)
        save_friends(self.friends)

    def _add_friend_named(self, name, offset):
        row = ClockRow(self.friends_frame, name, offset, on_remove=self._remove_friend)
        row.grid(row=len(self.friends), column=0, sticky="we", pady=2)
        self.friends.append(row)
        self.empty_lbl.grid_remove()

    def _use_computed(self):
        if self.diff_tab is not None and self.diff_tab.last_offset_min is not None:
            self.offset_entry.delete(0, "end")
            self.offset_entry.insert(0, format_offset(self.diff_tab.last_offset_min))

    def _remove_friend(self, row):
        row.destroy()
        self.friends.remove(row)
        for i, f in enumerate(self.friends):
            f.grid(row=i, column=0, sticky="we", pady=2)
        if not self.friends:
            self.empty_lbl.grid()
        save_friends(self.friends)

    def _tick(self):
        now = datetime.now()
        self.my_time_lbl.config(text=now.strftime("%H:%M:%S"))
        for f in self.friends:
            f.tick(now)
        self.after(1000 - now.microsecond // 1000, self._tick)


class CalcTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=16)
        self._sign = 1
        self._build()
        self._calculate()

    def _build(self):
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Start time:").grid(row=0, column=0, sticky="w")
        self.base_entry = PEntry(self, "e.g. 15:45 or 3:45 PM", width=22, font=("Consolas", 14))
        self.base_entry.grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.base_entry.bind("<KeyRelease>", lambda e: self._calculate())

        ttk.Label(self, text="Add or subtract a duration:").grid(row=2, column=0, sticky="w", pady=(12, 0))
        dur = ttk.Frame(self)
        dur.grid(row=3, column=0, sticky="w", pady=(4, 0))

        self.sign_btn = tk.Button(
            dur, text="+", width=3, relief="flat", bd=0,
            bg=PANEL2, fg=BLUE, activebackground="#3f3f46", activeforeground=BLUE,
            font=("Segoe UI", 13, "bold"), command=self._toggle_sign,
        )
        self.sign_btn.grid(row=0, column=0, padx=(0, 6))

        self.h_entry = PEntry(dur, "0", width=4, font=("Consolas", 14), justify="center")
        self.h_entry.grid(row=0, column=1)
        ttk.Label(dur, text="hours").grid(row=0, column=2, padx=(6, 10))

        self.m_entry = PEntry(dur, "0", width=4, font=("Consolas", 14), justify="center")
        self.m_entry.grid(row=0, column=3)
        ttk.Label(dur, text="minutes").grid(row=0, column=4, padx=(6, 0))

        self.h_entry.bind("<KeyRelease>", lambda e: self._calculate())
        self.m_entry.bind("<KeyRelease>", lambda e: self._calculate())

        self.res_main = ttk.Label(self, text="", font=("Consolas", 18, "bold"))
        self.res_main.grid(row=4, column=0, sticky="w", pady=(14, 0))
        self.res_alt = ttk.Label(self, text="", font=("Consolas", 13), foreground=MUTED)
        self.res_alt.grid(row=5, column=0, sticky="w", pady=(4, 0))

    def _toggle_sign(self):
        self._sign *= -1
        if self._sign < 0:
            self.sign_btn.config(text="\u2212", fg=RED, activeforeground=RED)
        else:
            self.sign_btn.config(text="+", fg=BLUE, activeforeground=BLUE)
        self._calculate()

    @staticmethod
    def _read_int(text):
        text = text.strip()
        if not text:
            return 0
        try:
            return int(text)
        except ValueError:
            return None

    def _calculate(self, event=None):
        raw = self.base_entry.get()
        if not raw.strip():
            self.res_main.config(text="")
            self.res_alt.config(text="")
            return
        base = parse_time(raw)
        if base is None:
            self.res_main.config(text="Enter a valid start time.", foreground=RED)
            self.res_alt.config(text="")
            return
        hours = self._read_int(self.h_entry.get())
        minutes = self._read_int(self.m_entry.get())
        if hours is None or minutes is None or minutes > 59:
            self.res_main.config(text="Invalid duration (minutes 0\u201359).", foreground=RED)
            self.res_alt.config(text="")
            return
        total = self._sign * (hours * 60 + minutes)
        base_dt = datetime(2000, 1, 2, base[0], base[1])
        res = base_dt + timedelta(minutes=total)
        days = (res.date() - base_dt.date()).days
        suffix = ""
        if days:
            label_part = f"{'+' if days > 0 else ''}{days} day{'s' if abs(days) != 1 else ''}"
            suffix = f"  ({label_part})"
        self.res_main.config(text=f"{res.hour:02d}:{res.minute:02d}{suffix}", foreground=GREEN)
        self.res_alt.config(text=f"{convert_to_12(res.hour, res.minute)}  12h")


def main():
    root = tk.Tk()
    root.title("Time Tool \u03a9 — AM/PM \u21c4 24h, Time Diff, Live Clocks, Time Calc")
    apply_dark_theme(root)

    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True)

    conv = ConverterTab(nb)
    diff = TimeDiffTab(nb)
    clocks = ClocksTab(nb, diff)
    calc = CalcTab(nb)

    nb.add(conv, text=" AM/PM \u21c4 24h ")
    nb.add(diff, text=" Time Difference ")
    nb.add(clocks, text=" Live Clocks ")
    nb.add(calc, text=" Time Calculator ")

    root.minsize(520, 340)
    saved = load_settings()
    if saved:
        root.geometry(saved)
    else:
        root.geometry("640x420")
    root.protocol("WM_DELETE_WINDOW", lambda: (save_settings(root), root.destroy()))
    root.bind("<Map>", lambda e: enable_dark_title_bar(root))
    root.after(120, lambda: enable_dark_title_bar(root))
    root.mainloop()


if __name__ == "__main__":
    main()