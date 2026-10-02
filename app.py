import sqlite3
import csv
from datetime import date
import customtkinter as ctk
from tkinter import messagebox, ttk

# Matplotlib integration for Tkinter
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# ==============================================================================
# DATABASE SETUP & INITIALIZATION
# ==============================================================================
DB_NAME = "student_system.db"

def connect_db():
    """Create SQLite database tables and populate sample data if empty."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            gender TEXT NOT NULL DEFAULT 'Male'
        )
    """)

    cursor.execute("PRAGMA table_info(students)")
    columns = [column[1] for column in cursor.fetchall()]
    if "gender" not in columns:
        cursor.execute("ALTER TABLE students ADD COLUMN gender TEXT NOT NULL DEFAULT 'Male'")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject TEXT NOT NULL,
            score REAL NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
        )
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        sample_students = [("101", "Alex Johnson", "Male"), ("102", "Sophia Smith", "Female"), ("103", "Liam Davis", "Male")]
        cursor.executemany("INSERT INTO students (roll_no, name, gender) VALUES (?, ?, ?)", sample_students)
        conn.commit()

        sample_scores = [
            (1, "Mathematics", 88.5),
            (1, "Science", 92.0),
            (2, "Mathematics", 74.0),
            (2, "Science", 81.0),
            (3, "Mathematics", 45.0),
            (3, "Science", 52.0),
        ]
        cursor.executemany("INSERT INTO performance (student_id, subject, score) VALUES (?, ?, ?)", sample_scores)

        today = str(date.today())
        sample_attendance = [
            (1, today, "100%"),
            (2, today, "100%"),
            (3, today, "0%"),
        ]
        cursor.executemany("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)", sample_attendance)
        conn.commit()

    conn.close()

def get_db_connection():
    return sqlite3.connect(DB_NAME)

connect_db()

# Default Theme Setup
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Color Palette Definitions (Shine Theme - Adaptive Dynamic Tuples)
SHINE_PRIMARY = "#2563eb"
SHINE_PRIMARY_HOVER = "#1d4ed8"
SHINE_GRADIENT_BG = ("#eef2ff", "#0f172a")       # Light Pearl / Dark Slate
SHINE_CARD_BG = ("#ffffff", "#1e293b")           # Light Card / Dark Card
SHINE_BORDER = ("#dbeafe", "#334155")            # Border accent
SHINE_TEXT_MAIN = ("#0f172a", "#f8fafc")         # High contrast text
SHINE_TEXT_MUTED = ("#64748b", "#94a3b8")        # Muted text
SHINE_INPUT_BG = ("#f8fafc", "#0f172a")          # Input fill
SHINE_ACCENT_CYAN = "#06b6d4"
SHINE_SUCCESS = "#10b981"
SHINE_WARNING = "#f59e0b"
SHINE_DANGER = "#ef4444"

# ==============================================================================
# MAIN APPLICATION INTERFACE
# ==============================================================================
class StudentTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ScholarSync — Student Directory & Analytics Portal")
        self.geometry("1280x820")
        self.minsize(1024, 680)
        self.configure(fg_color=SHINE_GRADIENT_BG)

        # Custom Styling for Treeview in Shine Theme
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.apply_treeview_styles()

        # Main Layout Grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar Navigation
        self.sidebar_frame = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=SHINE_CARD_BG, border_width=1, border_color=SHINE_BORDER)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        # App Brand Header
        brand_card = ctk.CTkFrame(self.sidebar_frame, fg_color=SHINE_GRADIENT_BG, corner_radius=12, border_width=1, border_color=SHINE_BORDER)
        brand_card.pack(fill="x", padx=16, pady=(20, 16))
        
        logo_label = ctk.CTkLabel(brand_card, text="⚡ ScholarSync", font=ctk.CTkFont(size=20, weight="bold"), text_color=SHINE_PRIMARY)
        logo_label.pack(anchor="w", padx=16, pady=(12, 2))
        
        sub_logo = ctk.CTkLabel(brand_card, text="PRO DIRECTORY EDITION", font=ctk.CTkFont(size=9, weight="bold"), text_color=SHINE_ACCENT_CYAN)
        sub_logo.pack(anchor="w", padx=16, pady=(0, 12))

        # Light / Dark Mode Toggle Switch
        theme_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=(0, 16))

        self.theme_switch = ctk.CTkSwitch(
            theme_frame, 
            text=" 🌙 Dark Mode", 
            command=self.toggle_theme,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=SHINE_TEXT_MAIN,
            progress_color=SHINE_PRIMARY
        )
        self.theme_switch.pack(anchor="w")

        # Navigation Buttons
        self.btn_students = ctk.CTkButton(self.sidebar_frame, text="  ❖ Manage Students", command=lambda: self.select_frame("students"), anchor="w", fg_color=SHINE_PRIMARY, hover_color=SHINE_PRIMARY_HOVER, text_color="#ffffff", height=46, corner_radius=10, font=ctk.CTkFont(size=13, weight="bold"))
        self.btn_students.pack(fill="x", padx=16, pady=6)

        self.btn_attendance = ctk.CTkButton(self.sidebar_frame, text="  ❖ Mark Attendance", command=lambda: self.select_frame("attendance"), anchor="w", fg_color="transparent", text_color=SHINE_TEXT_MUTED, hover_color=SHINE_GRADIENT_BG, height=46, corner_radius=10, font=ctk.CTkFont(size=13))
        self.btn_attendance.pack(fill="x", padx=16, pady=6)

        self.btn_performance = ctk.CTkButton(self.sidebar_frame, text="  ❖ Log Performance", command=lambda: self.select_frame("performance"), anchor="w", fg_color="transparent", text_color=SHINE_TEXT_MUTED, hover_color=SHINE_GRADIENT_BG, height=46, corner_radius=10, font=ctk.CTkFont(size=13))
        self.btn_performance.pack(fill="x", padx=16, pady=6)

        self.btn_reports = ctk.CTkButton(self.sidebar_frame, text="  ❖ Teacher Reports", command=lambda: self.select_frame("reports"), anchor="w", fg_color="transparent", text_color=SHINE_TEXT_MUTED, hover_color=SHINE_GRADIENT_BG, height=46, corner_radius=10, font=ctk.CTkFont(size=13))
        self.btn_reports.pack(fill="x", padx=16, pady=6)

        # Content Area Frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Tab Frames
        self.tab_students = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.tab_attendance = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.tab_performance = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.tab_reports = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        for frame in (self.tab_students, self.tab_attendance, self.tab_performance, self.tab_reports):
            frame.grid(row=0, column=0, sticky="nsew")

        self.setup_students_tab()
        self.setup_attendance_tab()
        self.setup_performance_tab()
        self.setup_reports_tab()

        self.select_frame("students")

    def toggle_theme(self):
        """Toggle between Light and Dark mode dynamically."""
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

        self.apply_treeview_styles()
        self.generate_report()

    def apply_treeview_styles(self):
        mode = ctk.get_appearance_mode()
        bg_color = "#1e293b" if mode == "Dark" else "#ffffff"
        fg_color = "#f8fafc" if mode == "Dark" else "#0f172a"
        header_bg = "#334155" if mode == "Dark" else "#e0e7ff"
        header_fg = "#ffffff" if mode == "Dark" else "#1e1b4b"

        self.style.configure(
            "Treeview", 
            rowheight=40, 
            font=("Segoe UI", 11), 
            background=bg_color, 
            fieldbackground=bg_color, 
            foreground=fg_color,
            borderwidth=0
        )
        self.style.configure(
            "Treeview.Heading", 
            font=("Segoe UI", 11, "bold"), 
            background=header_bg, 
            foreground=header_fg,
            relief="flat"
        )
        self.style.map("Treeview.Heading", background=[("active", "#c7d2fe")])

    def select_frame(self, name):
        for btn in [self.btn_students, self.btn_attendance, self.btn_performance, self.btn_reports]:
            btn.configure(fg_color="transparent", text_color=SHINE_TEXT_MUTED, font=ctk.CTkFont(size=13))

        if name == "students":
            self.btn_students.configure(fg_color=SHINE_PRIMARY, text_color="#ffffff", font=ctk.CTkFont(size=13, weight="bold"))
            self.tab_students.tkraise()
            self.load_students()
        elif name == "attendance":
            self.btn_attendance.configure(fg_color=SHINE_PRIMARY, text_color="#ffffff", font=ctk.CTkFont(size=13, weight="bold"))
            self.tab_attendance.tkraise()
        elif name == "performance":
            self.btn_performance.configure(fg_color=SHINE_PRIMARY, text_color="#ffffff", font=ctk.CTkFont(size=13, weight="bold"))
            self.tab_performance.tkraise()
        elif name == "reports":
            self.btn_reports.configure(fg_color=SHINE_PRIMARY, text_color="#ffffff", font=ctk.CTkFont(size=13, weight="bold"))
            self.tab_reports.tkraise()
            self.generate_report()

    # --- TAB 1: MANAGE STUDENTS ---
    def setup_students_tab(self):
        card = ctk.CTkFrame(self.tab_students, corner_radius=16, fg_color=SHINE_CARD_BG, border_width=1, border_color=SHINE_BORDER)
        card.pack(fill="x", padx=24, pady=20)

        ctk.CTkLabel(card, text="✦ Add New Student Profile", font=ctk.CTkFont(size=15, weight="bold"), text_color=SHINE_PRIMARY).pack(anchor="w", padx=24, pady=(20, 14))

        form_frame = ctk.CTkFrame(card, fg_color="transparent")
        form_frame.pack(fill="x", padx=24, pady=(0, 20))

        ctk.CTkLabel(form_frame, text="Roll Number:", text_color=SHINE_TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=(0, 10), sticky="w")
        self.entry_roll = ctk.CTkEntry(form_frame, width=130, placeholder_text="e.g. 101", fg_color=SHINE_INPUT_BG, border_color=SHINE_BORDER, text_color=SHINE_TEXT_MAIN, height=38)
        self.entry_roll.grid(row=0, column=1, padx=(0, 20))

        ctk.CTkLabel(form_frame, text="Full Name:", text_color=SHINE_TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=2, padx=(0, 10), sticky="w")
        self.entry_name = ctk.CTkEntry(form_frame, width=200, placeholder_text="e.g. Alex Johnson", fg_color=SHINE_INPUT_BG, border_color=SHINE_BORDER, text_color=SHINE_TEXT_MAIN, height=38)
        self.entry_name.grid(row=0, column=3, padx=(0, 20))

        ctk.CTkLabel(form_frame, text="Gender:", text_color=SHINE_TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=4, padx=(0, 10), sticky="w")
        self.combo_gender = ctk.CTkComboBox(form_frame, values=["Male", "Female"], width=110, state="readonly", fg_color=SHINE_INPUT_BG, border_color=SHINE_BORDER, text_color=SHINE_TEXT_MAIN, height=38)
        self.combo_gender.set("Male")
        self.combo_gender.grid(row=0, column=5, padx=(0, 20))

        btn_add = ctk.CTkButton(form_frame, text="+ Add Student", command=self.add_student, width=130, height=38, fg_color=SHINE_PRIMARY, hover_color=SHINE_PRIMARY_HOVER, font=ctk.CTkFont(size=12, weight="bold"))
        btn_add.grid(row=0, column=6)

        table_card = ctk.CTkFrame(self.tab_students, corner_radius=16, fg_color=SHINE_CARD_BG, border_width=1, border_color=SHINE_BORDER)
        table_card.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        table_header = ctk.CTkFrame(table_card, fg_color="transparent")
        table_header.pack(fill="x", padx=24, pady=(18, 14))

        ctk.CTkLabel(table_header, text="Registered Student Directory", font=ctk.CTkFont(size=16, weight="bold"), text_color=SHINE_TEXT_MAIN).pack(side="left")

        search_frame = ctk.CTkFrame(table_header, fg_color="transparent")
        search_frame.pack(side="right")

        self.entry_search = ctk.CTkEntry(search_frame, width=200, placeholder_text="🔍 Search name or roll...", fg_color=SHINE_INPUT_BG, border_color=SHINE_BORDER, text_color=SHINE_TEXT_MAIN, height=36)
        self.entry_search.pack(side="left", padx=(0, 8))
        self.entry_search.bind("<KeyRelease>", lambda e: self.load_students())

        btn_refresh_students = ctk.CTkButton(search_frame, text="Refresh", command=self.refresh_students_list, width=85, height=36, fg_color=SHINE_PRIMARY, hover_color=SHINE_PRIMARY_HOVER, font=ctk.CTkFont(size=12, weight="bold"))
        btn_refresh_students.pack(side="left")

        self.student_cards_container = ctk.CTkScrollableFrame(table_card, fg_color=SHINE_GRADIENT_BG, corner_radius=12)
        self.student_cards_container.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        self.student_cards_container.grid_columnconfigure((0, 1, 2), weight=1)

        self.load_students()

    def refresh_students_list(self):
        if hasattr(self, 'entry_search'):
            self.entry_search.delete(0, ctk.END)
        self.load_students()

    def add_student(self):
        roll = self.entry_roll.get().strip()
        name = self.entry_name.get().strip()
        gender = self.combo_gender.get().strip()

        if not roll or not name or not gender:
            messagebox.showwarning("Input Error", "Please fill in all fields!")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO students (roll_no, name, gender) VALUES (?, ?, ?)", (roll, name, gender))
            conn.commit()
            messagebox.showinfo("Success", "Student added successfully!")
            self.entry_roll.delete(0, ctk.END)
            self.entry_name.delete(0, ctk.END)
            self.combo_gender.set("Male")
            conn.close()
            self.load_students()
            self.update_dropdowns()
            self.generate_report()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Roll number already exists!")

    def load_students(self):
        for widget in self.student_cards_container.winfo_children():
            widget.destroy()
        
        search_query = self.entry_search.get().strip() if hasattr(self, 'entry_search') else ""
        
        conn = get_db_connection()
        cursor = conn.cursor()
        if search_query:
            cursor.execute("SELECT id, roll_no, name, gender FROM students WHERE name LIKE ? OR roll_no LIKE ? ORDER BY CAST(roll_no AS INTEGER) ASC, roll_no ASC", 
                           (f"%{search_query}%", f"%{search_query}%"))
        else:
            cursor.execute("SELECT id, roll_no, name, gender FROM students ORDER BY CAST(roll_no AS INTEGER) ASC, roll_no ASC")
            
        students = cursor.fetchall()
        conn.close()

        if not students:
            empty_lbl = ctk.CTkLabel(self.student_cards_container, text="No students registered yet.", font=ctk.CTkFont(size=13), text_color=SHINE_TEXT_MUTED)
            empty_lbl.grid(row=0, column=0, columnspan=3, pady=40)
            return

        for index, student in enumerate(students):
            s_id, roll, name, gender = student
            row_idx = index // 3
            col_idx = index % 3

            card = ctk.CTkFrame(self.student_cards_container, corner_radius=14, fg_color=SHINE_CARD_BG, border_width=1, border_color=SHINE_BORDER)
            card.grid(row=row_idx, column=col_idx, padx=10, pady=10, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)

            badge_bg = "#3b82f6" if gender == "Male" else "#ec4899"
            
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=16, pady=(14, 4))
            
            name_lbl = ctk.CTkLabel(top_row, text=name, font=ctk.CTkFont(size=14, weight="bold"), text_color=SHINE_TEXT_MAIN)
            name_lbl.pack(side="left")

            gender_badge = ctk.CTkLabel(top_row, text=f" {gender} ", font=ctk.CTkFont(size=10, weight="bold"), fg_color=badge_bg, text_color="#ffffff", corner_radius=6)
            gender_badge.pack(side="right")

            roll_lbl = ctk.CTkLabel(card, text=f"Roll No: #{roll}", font=ctk.CTkFont(size=12, weight="bold"), text_color=SHINE_TEXT_MUTED)
            roll_lbl.pack(anchor="w", padx=16, pady=(0, 14))

            btn_row = ctk.CTkFrame(card, fg_color="transparent")
            btn_row.pack(fill="x", padx=16, pady=(0, 14))

            btn_edit = ctk.CTkButton(btn_row, text="Edit", command=lambda s_id=s_id, roll=roll, name=name, gender=gender: self.edit_student_card(s_id, roll, name, gender), height=30, fg_color=SHINE_WARNING, hover_color="#d97706", font=ctk.CTkFont(size=11, weight="bold"))
            btn_edit.pack(side="left", fill="x", expand=True, padx=(0, 6))

            btn_delete = ctk.CTkButton(btn_row, text="Delete", command=lambda s_id=s_id, name=name: self.delete_student_card(s_id, name), height=30, fg_color=SHINE_DANGER, hover_color="#dc2626", font=ctk.CTkFont(size=11, weight="bold"))
            btn_delete.pack(side="right", fill="x", expand=True, padx=(6, 0))

    def edit_student_card(self, student_id, old_roll, old_name, old_gender):
        edit_win = ctk.CTkToplevel(self)
        edit_win.title("Edit Student Information")
        edit_win.geometry("400x300")
        edit_win.grab_set()

        ctk.CTkLabel(edit_win, text="Edit Student Profile", font=ctk.CTkFont(size=16, weight="bold"), text_color=SHINE_PRIMARY).pack(pady=18)

        f1 = ctk.CTkFrame(edit_win, fg_color="transparent")
        f1.pack(fill="x", padx=24, pady=6)
        ctk.CTkLabel(f1, text="Roll No:", width=90, anchor="w", text_color=SHINE_TEXT_MUTED).pack(side="left")
        e_roll = ctk.CTkEntry(f1, width=220, height=36, fg_color=SHINE_INPUT_BG, border_color=SHINE_BORDER, text_color=SHINE_TEXT_MAIN)
        e_roll.insert(0, str(old_roll))
        e_roll.pack(side="left")

        f2 = ctk.CTkFrame(edit_win, fg_color="transparent")
        f2.pack(fill="x", padx=24, pady=6)
        ctk.CTkLabel(f2, text="Name:", width=90, anchor="w", text_color=SHINE_TEXT_MUTED).pack(side="left")
        e_name = ctk.CTkEntry(f2, width=220, height=36, fg_color=SHINE_INPUT_BG, border_color=SHINE_BORDER, text_color=SHINE_TEXT_MAIN)
        e_name.insert(0, str(old_name))
        e_name.pack(side="left")

        f3 = ctk.CTkFrame(edit_win, fg_color="transparent")
        f3.pack(fill="x", padx=24, pady=6)
        ctk.CTkLabel(f3, text="Gender:", width=90, anchor="w", text_color=SHINE_TEXT_MUTED).pack(side="left")
        e_gender = ctk.CTkComboBox(f3, values=["Male", "Female"], width=220, height=36, state="readonly", fg_color=SHINE_INPUT_BG, border_color=SHINE_BORDER, text_color=SHINE_TEXT_MAIN)
        e_gender.set(str(old_gender))
        e_gender.pack(side="left")

        def save_edits():
            new_roll = e_roll.get().strip()
            new_name = e_name.get().strip()
            new_gender = e_gender.get().strip()

            if not new_roll or not new_name or not new_gender:
                messagebox.showwarning("Warning", "Fields cannot be empty.")
                return

            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE students SET roll_no = ?, name = ?, gender = ? WHERE id = ?", (new_roll, new_name, new_gender, student_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Student details updated!")
                edit_win.destroy()
                self.load_students()
                self.update_dropdowns()
                self.generate_report()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Roll number already exists!")

        ctk.CTkButton(edit_win, text="Save Changes", command=save_edits, height=38, fg_color=SHINE_PRIMARY, hover_color=SHINE_PRIMARY_HOVER, font=ctk.CTkFont(size=12, weight="bold")).pack(pady=18)

    def delete_student_card(self, student_id, student_name):
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {student_name}?\nAll record entries for this student will be removed.")
        if confirm:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Student profile deleted.")
            self.load_students()
            self.update_dropdowns()
            self.generate_report()

    # --- TAB 2: MARK ATTENDANCE ---
    def setup_attendance_tab(self):
        card = ctk.CTkFrame(self.tab_attendance, corner_radius=16, fg_color=SHINE_CARD_BG, border_width=1, border_color=SHINE_BORDER)
        card.pack(fill="x", padx=24, pady=24)

        ctk.CTkLabel(card, text="✦ Mark Daily Attendance Rate", font=ctk.CTkFont(size=16, weight="bold"), text_color=SHINE_PRIMARY).pack(anchor="w", padx=24, pady=(22, 16))

        form_frame = ctk.CTkFrame(card, fg_color="transparent")
        form_frame.pack(fill="x", padx=24, pady=(0, 24))

        ctk.CTkLabel(form_frame, text="Select Student:", text_color=SHINE_TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=(0, 10), sticky="w")
        self.combo_att_student = ctk.CTkComboBox(form_frame, width=280, state="readonly", fg_color=SHINE_INPUT_BG, border_color=SHINE_BORDER, text_color=SHINE_TEXT_MAIN, height=38)
        self.combo_att_student.grid(row=0, column=1, padx=(0, 25))

        ctk.CTkLabel(form_frame, text="Attendance Rate:", text_color=SHINE_TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=2, padx=(0, 10), sticky="w")

        stepper_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        stepper_frame.grid(row=0, column=3, padx=(0, 25))

        btn_minus = ctk.CTkButton(stepper_frame, text="-", width=36, height=38, command=self.decrease_attendance_pct, fg_color=SHINE_BORDER, hover_color="#cbd5e1", text_color=SHINE_TEXT_MAIN, font=ctk.CTkFont(size=14, weight="bold"))
        btn_minus.pack(side="left", padx=(0, 4))

        self.entry_att_pct = ctk.CTkEntry(stepper_frame, width=70, height=38, justify="center", fg_color=SHINE_INPUT_BG, border_color=SHINE_BORDER, text_color=SHINE_TEXT_MAIN, font=ctk.CTkFont(size=13, weight="bold"))
        self.entry_att_pct.insert(0, "100%")
        self.entry_att_pct.pack(side="left", padx=(0, 4))

        btn_plus = ctk.CTkButton(stepper_frame, text="+", width=36, height=38, command=self.increase_attendance_pct, fg_color=SHINE_BORDER, hover_color="#cbd5e1", text_color=SHINE_TEXT_MAIN, font=ctk.CTkFont(size=14, weight="bold"))
        btn_plus.pack(side="left")

        btn_mark = ctk.CTkButton(form_frame, text="Save Attendance", command=self.save_attendance, width=140, height=38, fg_color=SHINE_PRIMARY, hover_color=SHINE_PRIMARY_HOVER, font=ctk.CTkFont(size=12, weight="bold"))
        btn_mark.grid(row=0, column=4)

    def increase_attendance_pct(self):
        try:
            val_str = self.entry_att_pct.get().replace("%", "").strip()
            val = int(val_str)
            val = min(100, val + 5)
            self.entry_att_pct.delete(0, ctk.END)
            self.entry_att_pct.insert(0, f"{val}%")
        except ValueError:
            self.entry_att_pct.delete(0, ctk.END)
            self.entry_att_pct.insert(0, "100%")

    def decrease_attendance_pct(self):
        try:
            val_str = self.entry_att_pct.get().replace("%", "").strip()
            val = int(val_str)
            val = max(0, val - 5)
            self.entry_att_pct.delete(0, ctk.END)
            self.entry_att_pct.insert(0, f"{val}%")
        except ValueError:
            self.entry_att_pct.delete(0, ctk.END)
            self.entry_att_pct.insert(0, "0%")

    def save_attendance(self):
        student_str = self.combo_att_student.get()
        status_pct = self.entry_att_pct.get().strip()
        if not student_str:
            messagebox.showwarning("Warning", "Select a student!")
            return
        
        student_id = student_str.split(" - ")[0]
        today = str(date.today())

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)", (student_id, today, status_pct))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Attendance logged as {status_pct} for today ({today})!")
        self.generate_report()

    # --- TAB 3: LOG PERFORMANCE ---
    def setup_performance_tab(self):
        card = ctk.CTkFrame(self.tab_performance, corner_radius=16, fg_color=SHINE_CARD_BG, border_width=1, border_color=SHINE_BORDER)
        card.pack(fill="x", padx=24, pady=24)

        ctk.CTkLabel(card, text="✦ Record Student Academic Performance", font=ctk.CTkFont(size=16, weight="bold"), text_color=SHINE_PRIMARY).pack(anchor="w", padx=24, pady=(22, 16))

        form_frame = ctk.CTkFrame(card, fg_color="transparent")
        form_frame.pack(fill="x", padx=24, pady=(0, 24))

        ctk.CTkLabel(form_frame, text="Select Student:", text_color=SHINE_TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=(0, 10), pady=10, sticky="w")
        self.combo_perf_student = ctk.CTkComboBox(form_frame, width=320, state="readonly", fg_color=SHINE_INPUT_BG, border_color=SHINE_BORDER, text_color=SHINE_TEXT_MAIN, height=38)
        self.combo_perf_student.grid(row=0, column=1, columnspan=3, padx=(0, 30), pady=10, sticky="w")

        ctk.CTkLabel(form_frame, text="Subject Name:", text_color=SHINE_TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, padx=(0, 10), pady=10, sticky="w")
        self.entry_subject = ctk.CTkEntry(form_frame, width=220, placeholder_text="e.g. Mathematics", fg_color=SHINE_INPUT_BG, border_color=SHINE_BORDER, text_color=SHINE_TEXT_MAIN, height=38)
        self.entry_subject.grid(row=1, column=1, padx=(0, 30), pady=10, sticky="w")

        ctk.CTkLabel(form_frame, text="Score (0-100):", text_color=SHINE_TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=2, padx=(0, 10), pady=10, sticky="w")
        self.entry_score = ctk.CTkEntry(form_frame, width=130, placeholder_text="e.g. 85", fg_color=SHINE_INPUT_BG, border_color=SHINE_BORDER, text_color=SHINE_TEXT_MAIN, height=38)
        self.entry_score.grid(row=1, column=3, padx=(0, 30), pady=10, sticky="w")

        btn_score = ctk.CTkButton(form_frame, text="Save Score", command=self.save_performance, width=140, height=38, fg_color=SHINE_PRIMARY, hover_color=SHINE_PRIMARY_HOVER, font=ctk.CTkFont(size=12, weight="bold"))
        btn_score.grid(row=1, column=4, pady=10)

    def save_performance(self):
        student_str = self.combo_perf_student.get()
        subject = self.entry_subject.get().strip()
        score = self.entry_score.get().strip()

        if not student_str or not subject or not score:
            messagebox.showwarning("Warning", "All fields are required!")
            return

        student_id = student_str.split(" - ")[0]
        try:
            score_val = float(score)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO performance (student_id, subject, score) VALUES (?, ?, ?)", (student_id, subject, score_val))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Performance score saved!")
            self.entry_subject.delete(0, ctk.END)
            self.entry_score.delete(0, ctk.END)
            self.generate_report()
        except ValueError:
            messagebox.showerror("Error", "Score must be a valid number!")

    # --- TAB 4: TEACHER REPORTS & ANALYTICS ---
    def setup_reports_tab(self):
        kpi_frame = ctk.CTkFrame(self.tab_reports, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=24, pady=(16, 0))

        self.card_total = self.create_kpi_card(kpi_frame, "TOTAL STUDENTS", "0", SHINE_PRIMARY)
        self.card_total.pack(side="left", fill="x", expand=True, padx=6)

        self.card_att = self.create_kpi_card(kpi_frame, "AVG CLASS ATTENDANCE", "0.0%", SHINE_SUCCESS)
        self.card_att.pack(side="left", fill="x", expand=True, padx=6)

        self.card_score = self.create_kpi_card(kpi_frame, "OVERALL GRADE AVERAGE", "0.0", SHINE_WARNING)
        self.card_score.pack(side="left", fill="x", expand=True, padx=6)

        self.chart_frame = ctk.CTkFrame(self.tab_reports, corner_radius=16, fg_color=SHINE_CARD_BG, border_width=1, border_color=SHINE_BORDER)
        self.chart_frame.pack(fill="x", padx=24, pady=12)

        card = ctk.CTkFrame(self.tab_reports, corner_radius=16, fg_color=SHINE_CARD_BG, border_width=1, border_color=SHINE_BORDER)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        top_bar = ctk.CTkFrame(card, fg_color="transparent")
        top_bar.pack(fill="x", padx=24, pady=14)

        ctk.CTkLabel(top_bar, text="Student Directory Analytics (Double-click row for details)", font=ctk.CTkFont(size=14, weight="bold"), text_color=SHINE_TEXT_MAIN).pack(side="left")
        
        btn_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_frame.pack(side="right")

        btn_export = ctk.CTkButton(btn_frame, text="Export CSV", command=self.export_csv, width=120, height=36, fg_color=SHINE_SUCCESS, hover_color="#059669", font=ctk.CTkFont(size=12, weight="bold"))
        btn_export.pack(side="left", padx=(0, 10))

        btn_refresh = ctk.CTkButton(btn_frame, text="Refresh Data", command=self.generate_report, width=120, height=36, fg_color=SHINE_PRIMARY, hover_color=SHINE_PRIMARY_HOVER, font=ctk.CTkFont(size=12, weight="bold"))
        btn_refresh.pack(side="left")

        tree_frame = ctk.CTkFrame(card, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        self.tree_reports = ttk.Treeview(tree_frame, columns=("Roll", "Name", "Gender", "Total Logs", "Avg Att %", "Avg Score", "Status"), show="headings")
        headings = ["Roll No", "Student Name", "Gender", "Logs Count", "Avg Attendance %", "Average Score", "Academic Flag"]
        col_ids = ("Roll", "Name", "Gender", "Total Logs", "Avg Att %", "Avg Score", "Status")
        
        for cid, text in zip(col_ids, headings):
            self.tree_reports.heading(cid, text=text)
            self.tree_reports.column(cid, width=110, anchor="center")
        
        self.tree_reports.column("Roll", anchor="w", width=110)
        self.tree_reports.column("Name", width=200, anchor="w")
        self.tree_reports.column("Gender", width=100, anchor="center")
        self.tree_reports.column("Status", width=140, anchor="center")

        self.tree_reports.bind("<Double-1>", self.open_student_detail)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_reports.yview)
        self.tree_reports.configure(yscrollcommand=scrollbar.set)

        self.tree_reports.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_kpi_card(self, parent, title, initial_value, accent_color):
        frame = ctk.CTkFrame(parent, corner_radius=14, fg_color=SHINE_CARD_BG, border_width=1, border_color=SHINE_BORDER)
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=10, weight="bold"), text_color=SHINE_TEXT_MUTED).pack(anchor="w", padx=18, pady=(12, 2))
        val_label = ctk.CTkLabel(frame, text=initial_value, font=ctk.CTkFont(size=24, weight="bold"), text_color=accent_color)
        val_label.pack(anchor="w", padx=18, pady=(0, 12))
        frame.val_label = val_label
        return frame

    def render_charts(self, student_names, avg_scores, att_percentages):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if not student_names:
            return

        mode = ctk.get_appearance_mode()
        bg_face = '#1e293b' if mode == 'Dark' else '#ffffff'
        axis_face = '#0f172a' if mode == 'Dark' else '#f8fafc'
        text_color = '#f8fafc' if mode == 'Dark' else '#1e293b'
        subtext_color = '#94a3b8' if mode == 'Dark' else '#475569'

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 2.1), dpi=100)
        fig.patch.set_facecolor(bg_face)

        ax1.set_facecolor(axis_face)
        ax1.bar(student_names, avg_scores, color=SHINE_PRIMARY, width=0.45)
        ax1.set_title('Average Performance Score', fontsize=10, fontweight='bold', color=text_color)
        ax1.set_ylim(0, 100)
        ax1.tick_params(axis='x', rotation=15, labelsize=8, colors=subtext_color)
        ax1.tick_params(axis='y', labelsize=8, colors=subtext_color)
        for spine in ax1.spines.values():
            spine.set_color('#475569' if mode == 'Dark' else '#cbd5e1')

        ax2.set_facecolor(axis_face)
        ax2.bar(student_names, att_percentages, color=SHINE_SUCCESS, width=0.45)
        ax2.set_title('Average Attendance Rate (%)', fontsize=10, fontweight='bold', color=text_color)
        ax2.set_ylim(0, 100)
        ax2.tick_params(axis='x', rotation=15, labelsize=8, colors=subtext_color)
        ax2.tick_params(axis='y', labelsize=8, colors=subtext_color)
        for spine in ax2.spines.values():
            spine.set_color('#475569' if mode == 'Dark' else '#cbd5e1')

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=8)

    def generate_report(self):
        for item in self.tree_reports.get_children():
            self.tree_reports.delete(item)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, roll_no, name, gender FROM students ORDER BY CAST(roll_no AS INTEGER) ASC, roll_no ASC")
        students = cursor.fetchall()

        total_students = len(students)
        sum_att = 0.0
        att_count = 0
        sum_scores = 0.0
        score_count = 0

        chart_names = []
        chart_scores = []
        chart_atts = []

        for s in students:
            s_id, roll, name, gender = s

            cursor.execute("SELECT status FROM attendance WHERE student_id = ?", (s_id,))
            att_rows = cursor.fetchall()
            total_logs = len(att_rows)

            running_att_sum = 0.0
            for r in att_rows:
                val_raw = str(r[0]).replace("%", "").strip()
                try:
                    running_att_sum += float(val_raw)
                except ValueError:
                    if r[0] == "Present":
                        running_att_sum += 100.0

            avg_att_val = (running_att_sum / total_logs) if total_logs > 0 else 0.0
            if total_logs > 0:
                sum_att += avg_att_val
                att_count += 1

            att_pct_str = f"{avg_att_val:.1f}%" if total_logs > 0 else "N/A"

            cursor.execute("SELECT AVG(score) FROM performance WHERE student_id = ?", (s_id,))
            avg_score = cursor.fetchone()[0]
            avg_val = avg_score if avg_score is not None else 0
            if avg_score is not None:
                sum_scores += avg_val
                score_count += 1

            avg_str = f"{avg_val:.1f}" if avg_score is not None else "N/A"

            flag = "Good Standing"
            if (total_logs > 0 and avg_att_val < 75) or (avg_score is not None and avg_val < 50):
                flag = "Needs Attention"
            elif total_logs == 0 and avg_score is None:
                flag = "No Data"

            self.tree_reports.insert("", ctk.END, values=(roll, name, gender, total_logs, att_pct_str, avg_str, flag))

            chart_names.append(name)
            chart_scores.append(avg_val)
            chart_atts.append(avg_att_val)

        conn.close()

        self.card_total.val_label.configure(text=str(total_students))
        avg_overall_att = (sum_att / att_count) if att_count > 0 else 0.0
        self.card_att.val_label.configure(text=f"{avg_overall_att:.1f}%")
        avg_overall_score = (sum_scores / score_count) if score_count > 0 else 0.0
        self.card_score.val_label.configure(text=f"{avg_overall_score:.1f}")

        self.render_charts(chart_names, chart_scores, chart_atts)

    def open_student_detail(self, event):
        selected_item = self.tree_reports.selection()
        if not selected_item:
            return
        
        row_values = self.tree_reports.item(selected_item)["values"]
        roll_no = row_values[0]
        student_name = row_values[1]
        student_gender = row_values[2]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM students WHERE roll_no = ?", (roll_no,))
        res = cursor.fetchone()
        if not res:
            conn.close()
            return
        student_id = res[0]

        cursor.execute("SELECT date, status FROM attendance WHERE student_id = ? ORDER BY date DESC", (student_id,))
        attendance_records = cursor.fetchall()

        cursor.execute("SELECT subject, score FROM performance WHERE student_id = ?", (student_id,))
        performance_records = cursor.fetchall()
        conn.close()

        popup = ctk.CTkToplevel(self)
        popup.title(f"Student Profile — {student_name}")
        popup.geometry("480x530")
        popup.minsize(420, 480)
        popup.grab_set()

        ctk.CTkLabel(popup, text=f"Profile Details: {student_name}", font=ctk.CTkFont(size=16, weight="bold"), text_color=SHINE_PRIMARY).pack(padx=24, pady=(22, 4))
        ctk.CTkLabel(popup, text=f"Roll Number: #{roll_no}  •  Gender: {student_gender}", font=ctk.CTkFont(size=13), text_color=SHINE_TEXT_MUTED).pack(padx=24, pady=(0, 14))

        ctk.CTkLabel(popup, text="Subject Scores", font=ctk.CTkFont(size=13, weight="bold"), text_color=SHINE_PRIMARY).pack(anchor="w", padx=28)
        perf_frame = ctk.CTkScrollableFrame(popup, height=120, fg_color=SHINE_GRADIENT_BG, corner_radius=10)
        perf_frame.pack(fill="x", padx=24, pady=5)
        if performance_records:
            for sub, sc in performance_records:
                ctk.CTkLabel(perf_frame, text=f"• {sub}: {sc}/100", font=ctk.CTkFont(size=12), text_color=SHINE_TEXT_MAIN).pack(anchor="w", padx=10, pady=2)
        else:
            ctk.CTkLabel(perf_frame, text="No performance records logged.", text_color=SHINE_TEXT_MUTED).pack(anchor="w", padx=10, pady=5)

        ctk.CTkLabel(popup, text="Attendance History", font=ctk.CTkFont(size=13, weight="bold"), text_color=SHINE_PRIMARY).pack(anchor="w", padx=28, pady=(10, 0))
        att_frame = ctk.CTkScrollableFrame(popup, height=130, fg_color=SHINE_GRADIENT_BG, corner_radius=10)
        att_frame.pack(fill="x", padx=24, pady=5)
        if attendance_records:
            for dt, st in attendance_records:
                clean_st = st if "%" in str(st) else f"{st}%"
                ctk.CTkLabel(att_frame, text=f"• {dt} — Attendance: {clean_st}", font=ctk.CTkFont(size=12), text_color=SHINE_TEXT_MAIN).pack(anchor="w", padx=10, pady=2)
        else:
            ctk.CTkLabel(att_frame, text="No attendance logs recorded.", text_color=SHINE_TEXT_MUTED).pack(anchor="w", padx=10, pady=5)

        ctk.CTkButton(popup, text="Close Window", command=popup.destroy, fg_color=SHINE_BORDER, hover_color="#cbd5e1", text_color=SHINE_TEXT_MAIN, width=120, height=36).pack(pady=15)

    def export_csv(self):
        file_path = "student_analytics_report.csv"
        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Roll No", "Student Name", "Gender", "Total Logs", "Avg Attendance %", "Average Score", "Academic Flag"])
                for row_id in self.tree_reports.get_children():
                    row_values = self.tree_reports.item(row_id)["values"]
                    writer.writerow(row_values)
            messagebox.showinfo("Export Successful", f"Report saved as '{file_path}' in your working directory!")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export file: {e}")

    def update_dropdowns(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, roll_no, name, gender FROM students ORDER BY CAST(roll_no AS INTEGER) ASC, roll_no ASC")
            students = cursor.fetchall()
            conn.close()

            student_options = [f"{s[0]} - {s[2]} ({s[1]})" for s in students]
            self.combo_att_student.configure(values=student_options)
            self.combo_perf_student.configure(values=student_options)
            if student_options:
                self.combo_att_student.set(student_options[0])
                self.combo_perf_student.set(student_options[0])
        except Exception:
            pass


if __name__ == "__main__":
    app = StudentTrackerApp()
    app.update_dropdowns()
    app.mainloop()