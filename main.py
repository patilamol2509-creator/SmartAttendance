#!/usr/bin/env python3
"""
Rewritten main.py — safer DB initialization, explicit SQL, and minor hardening.
Intended as a drop-in replacement for the original main.py.
"""
import os
import sqlite3
from datetime import datetime
from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

# Optional scanner; app works without it.
try:
    from kivy_garden.zbarcam import ZBarCam
except Exception:
    ZBarCam = None

BG = (.95, .97, .99, 1)
NAVY = (.07, .13, .25, 1)
BLUE = (.12, .34, .78, 1)
TEAL = (.04, .61, .58, 1)
WHITE = (1, 1, 1, 1)
TEXT = (.14, .19, .28, 1)
MUTED = (.42, .48, .57, 1)
PALE = (.90, .94, .99, 1)


class Card(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.padding = dp(13)
        self.spacing = dp(7)
        with self.canvas.before:
            Color(*WHITE)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(15)])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size


class DB:
    def __init__(self, path):
        # ensure directory exists; fallback to current dir if dirname is empty
        dirpath = os.path.dirname(path) or os.getcwd()
        os.makedirs(dirpath, exist_ok=True)

        # connect and enable foreign keys
        self.conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row

        # create tables with UNIQUE constraint to prevent duplicate marking per day
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                roll TEXT UNIQUE NOT NULL,
                class_name TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY,
                student_id INTEGER NOT NULL,
                day TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT DEFAULT 'Present',
                UNIQUE(student_id, day),
                FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
            );
            """
        )
        self.conn.commit()

    def add(self, name, roll, class_name):
        with self.conn:
            self.conn.execute(
                "INSERT INTO students(name, roll, class_name) VALUES (?, ?, ?)",
                (name.strip(), roll.strip(), class_name.strip()),
            )

    def students(self):
        cur = self.conn.execute("SELECT name, roll, class_name FROM students ORDER BY roll")
        return cur.fetchall()

    def count(self):
        cur = self.conn.execute("SELECT COUNT(*) AS c FROM students")
        return cur.fetchone()["c"]

    def today(self):
        cur = self.conn.execute("SELECT COUNT(*) AS c FROM attendance WHERE day = ?", (datetime.now().strftime("%Y-%m-%d"),))
        return cur.fetchone()["c"]

    def mark(self, roll):
        cur = self.conn.execute("SELECT id, name, roll FROM students WHERE roll = ?", (roll.strip(),))
        s = cur.fetchone()
        if not s:
            return False, f"Roll number {roll} is not registered."
        n = datetime.now()
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO attendance(student_id, day, time) VALUES (?, ?, ?)",
                    (s["id"], n.strftime("%Y-%m-%d"), n.strftime("%H:%M:%S")),
                )
            return True, f"{s['name']} (Roll {s['roll']})\n{n.strftime('%d %b %Y • %I:%M %p')}"
        except sqlite3.IntegrityError:
            return False, f"{s['name']} is already marked present today."

    def history(self, limit=150):
        cur = self.conn.execute(
            "SELECT s.name AS name, s.roll AS roll, s.class_name AS class_name, a.day AS day, a.time AS time, a.status AS status "
            "FROM attendance a JOIN students s ON s.id = a.student_id ORDER BY a.id DESC LIMIT ?",
            (limit,),
        )
        return cur.fetchall()


class SmartAttendance(App):
    def build(self):
        self.title = "Smart Attendance"
        Window.clearcolor = BG
        self.db = DB(os.path.join(self.user_data_dir, "attendance.db"))
        self.page = BoxLayout(orientation="vertical", spacing=0)
        self.body = BoxLayout(orientation="vertical", padding=[dp(15), dp(13)], spacing=dp(11))
        self.page.add_widget(self.body)

        nav = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(6), padding=dp(7))
        for t, f in [("⌂ Home", self.home), ("＋ Student", self.register), ("▤ History", self.history)]:
            b = Button(text=t, background_normal="", background_color=PALE, color=NAVY, font_size="13sp")
            b.bind(on_release=lambda _b, fn=f: fn())
            nav.add_widget(b)
        self.page.add_widget(nav)

        self.home()
        return self.page

    def clear(self):
        self.body.clear_widgets()

    def lbl(self, text, size=14, color=TEXT, bold=False, height=30, align="left"):
        l = Label(text=text, font_size=f"{size}sp", color=color, bold=bold, size_hint_y=None, height=dp(height), halign=align, valign="middle")
        l.bind(size=lambda o, v: setattr(o, "text_size", (v[0], None)))
        return l

    def btn(self, text, fn, primary=True, height=48):
        b = Button(
            text=text,
            size_hint_y=None,
            height=dp(height),
            background_normal="",
            background_color=BLUE if primary else PALE,
            color=WHITE if primary else NAVY,
            bold=True,
            font_size="14sp",
        )
        b.bind(on_release=lambda *_: fn())
        return b

    def popup(self, title, msg, success=False):
        box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        box.add_widget(Label(text=msg, color=TEXT, halign="center"))
        b = Button(text="Continue", size_hint_y=None, height=dp(44), background_normal="", background_color=TEAL if success else BLUE, color=WHITE)
        box.add_widget(b)
        p = Popup(title=title, content=box, size_hint=(.88, .38))
        b.bind(on_release=p.dismiss)
        p.open()

    def header(self, sub):
        self.body.add_widget(self.lbl("[b]SMART ATTENDANCE[/b]", 22, NAVY, True, 36))
        self.body.add_widget(self.lbl(sub, 12, MUTED, False, 24))

    def stat(self, title, val, note):
        c = Card(orientation="vertical", size_hint_y=None, height=dp(105))
        c.add_widget(self.lbl(title, 11, MUTED, True, 22))
        c.add_widget(self.lbl(str(val), 26, NAVY, True, 36))
        c.add_widget(self.lbl(note, 10, MUTED, False, 20))
        return c

    def home(self):
        self.clear()
        self.header("Offline QR-based student attendance")
        grid = GridLayout(cols=2, spacing=dp(9), size_hint_y=None, height=dp(112))
        grid.add_widget(self.stat("REGISTERED STUDENTS", self.db.count(), "Stored on this phone"))
        grid.add_widget(self.stat("PRESENT TODAY", self.db.today(), "Today's attendance"))
        self.body.add_widget(grid)

        c = Card(orientation="vertical", size_hint_y=None, height=dp(174))
        c.add_widget(self.lbl("Ready to take attendance?", 18, NAVY, True, 30))
        c.add_widget(self.lbl("Scan a student's QR code to record attendance automatically.", 12, MUTED, False, 38))
        c.add_widget(self.btn("▦   SCAN QR CODE", self.scan, True, 52))
        self.body.add_widget(c)

        a = Card(orientation="vertical", size_hint_y=None, height=dp(142))
        a.add_widget(self.lbl("QUICK ACTIONS", 12, MUTED, True, 22))
        a.add_widget(self.btn("＋  Register New Student", self.register, False, 43))
        a.add_widget(self.btn("▤  View Attendance History", self.history, False, 43))
        self.body.add_widget(a)

        self.body.add_widget(self.lbl("Works offline • Data stored in SQLite", 11, MUTED, False, 24, "center"))

    def register(self):
        self.clear()
        self.header("Add a student to your local register")
        c = Card(orientation="vertical", size_hint_y=None, height=dp(306))
        c.add_widget(self.lbl("STUDENT DETAILS", 12, MUTED, True, 22))
        n = TextInput(hint_text="Full name", multiline=False, size_hint_y=None, height=dp(46), background_color=BG, foreground_color=TEXT, padding=dp(10))
        r = TextInput(hint_text="Roll number (e.g. 101)", multiline=False, size_hint_y=None, height=dp(46), background_color=BG, foreground_color=TEXT, padding=dp(10))
        cl = TextInput(hint_text="Class / division (optional)", multiline=False, size_hint_y=None, height=dp(46), background_color=BG, foreground_color=TEXT, padding=dp(10))
        for w in (n, r, cl):
            c.add_widget(w)

        def save():
            if not n.text.strip() or not r.text.strip():
                self.popup("Missing details", "Enter name and roll number.")
                return
            try:
                self.db.add(n.text, r.text, cl.text)
                self.popup("Student registered", n.text.strip() + " has been added.", True)
                self.home()
            except sqlite3.IntegrityError:
                self.popup("Duplicate roll number", "This roll number is already registered.")

        c.add_widget(self.btn("SAVE STUDENT", save, True, 46))
        self.body.add_widget(c)
        self.body.add_widget(self.btn("Back to Dashboard", self.home, False, 44))

    def scan(self):
        self.clear()
        self.header("Scan a student QR code")
        c = Card(orientation="vertical", size_hint_y=None, height=dp(245))
        if ZBarCam:
            try:
                self.cam = ZBarCam(size_hint_y=.75)
                self.cam.bind(symbols=self.on_symbols)
                c.add_widget(self.cam)
                c.add_widget(self.lbl("Point camera at QR code", 12, MUTED, False, 28, "center"))
            except Exception as e:
                c.add_widget(self.lbl("Scanner error: " + str(e), 11, MUTED, False, 55))
        else:
            c.add_widget(self.lbl("Camera scanner module unavailable in this run.", 12, MUTED, False, 55, "center"))
            c.add_widget(self.lbl("Use the QR text field below for testing.", 12, MUTED, False, 40, "center"))
        self.body.add_widget(c)

        self.body.add_widget(self.lbl("QR FORMAT", 11, MUTED, True, 22))
        self.qr = TextInput(hint_text="STUDENT:101", multiline=False, size_hint_y=None, height=dp(46), background_color=WHITE, foreground_color=TEXT, padding=dp(10))
        self.body.add_widget(self.qr)
        self.body.add_widget(self.btn("PROCESS QR TEXT", lambda: self.process(self.qr.text), True, 46))
        self.body.add_widget(self.btn("Back to Dashboard", self.home, False, 42))

    def on_symbols(self, scanner, symbols):
        if not symbols:
            return
        raw = symbols[0].data
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", "ignore")
        if getattr(self, "last_qr", None) == raw:
            return
        self.last_qr = raw
        Clock.schedule_once(lambda _dt: self.process(raw), 0)

    def process(self, raw):
        raw = (raw or "").strip()
        if not raw.upper().startswith("STUDENT:"):
            self.popup("Invalid QR", "Expected STUDENT:<roll_number>")
            self.last_qr = None
            return
        roll = raw.split(":", 1)[1].strip()
        if not roll:
            self.popup("Invalid QR", "Roll number is missing.")
            return
        ok, msg = self.db.mark(roll)
        self.last_qr = None
        self.popup("Attendance marked" if ok else "Not marked", msg, ok)

    def history(self):
        self.clear()
        self.header("Attendance records saved on this phone")
        rows = self.db.history()
        if not rows:
            self.body.add_widget(self.lbl("No attendance records yet.", 14, MUTED, False, 70, "center"))
        else:
            sv = ScrollView()
            stack = GridLayout(cols=1, spacing=dp(7), size_hint_y=None)
            stack.bind(minimum_height=stack.setter("height"))
            for row in rows:
                n = row["name"]
                r = row["roll"]
                cl = row["class_name"]
                d = row["day"]
                t = row["time"]
                s = row["status"]
                c = Card(orientation="vertical", size_hint_y=None, height=dp(72))
                c.add_widget(self.lbl(f"{n} • Roll {r}", 13, NAVY, True, 25))
                c.add_widget(self.lbl(f"{d} {t} • {s} • {cl or 'Class not set'}", 10, MUTED, False, 23))
                stack.add_widget(c)
            sv.add_widget(stack)
            self.body.add_widget(sv)
        self.body.add_widget(self.btn("Back to Dashboard", self.home, False, 44))


if __name__ == "__main__":
    SmartAttendance().run()
