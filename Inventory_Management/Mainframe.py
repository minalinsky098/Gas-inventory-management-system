import tkinter as tk
from PIL import Image, ImageTk 
from tkinter import messagebox, simpledialog, ttk
import datetime
import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def setup_database():
    conn = sqlite3.connect('Databases/inventory_db.db')
    cursor = conn.cursor()
    # Create db tables 
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shift (
            shift_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            shift_date DATETIME,
            shift_type TEXT,
            shift_start_time DATETIME,
            shift_end_time DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fuel_type (
            fuel_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fuel_name TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pump (
            pump_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fuel_type_id INTEGER NOT NULL,
            pump_label TEXT NOT NULL,
            FOREIGN KEY (fuel_type_id) REFERENCES fuel_type(fuel_type_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            shift_id INTEGER NOT NULL,
            pump_id INTEGER NOT NULL,
            Volume REAL NOT NULL,
            Date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shift_id) REFERENCES shift(shift_id)
        )
    ''')
    
    # --- Pre-populate fuel_type table if empty ---
    cursor.execute('SELECT COUNT(*) FROM fuel_type')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO fuel_type (fuel_name) VALUES (?)', ('Diesel',))
        diesel_id = cursor.lastrowid
        cursor.execute('INSERT INTO fuel_type (fuel_name) VALUES (?)', ('Premium',))
        premium_id = cursor.lastrowid
        cursor.execute('INSERT INTO fuel_type (fuel_name) VALUES (?)', ('Unleaded',))
        unleaded_id = cursor.lastrowid

       
        pumps = [
            (diesel_id, 'Diesel 1'), 
            (diesel_id, 'Diesel 2'), 
            (premium_id, 'Premium 1'), 
            (premium_id, 'Premium 2'), 
            (premium_id, 'Premium 3'), 
            (unleaded_id, 'Unleaded')
        ]
        cursor.executemany("INSERT INTO pump (fuel_type_id, pump_label) VALUES (?, ?)", pumps)
    
    #new admin setup
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        
        root = tk.Tk()
        root.withdraw()  
        new_admin_password = None
        while not new_admin_password:
            new_admin_password = simpledialog.askstring(
                "Set Admin Password",
                "Username: Admin\nPlease set a password for the default admin user:",
                show='*'
            )
        cursor.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
        ('admin', hash_password(new_admin_password))
        )
        cursor.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            ('user123', hash_password('qwertyuiop'))  #employee user setup
        )
        root.destroy()

    conn.commit()
    conn.close()

def check_login(username, password):
    conn = sqlite3.connect('Databases/inventory_db.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, password_hash FROM users WHERE username=?', (username,))
    dbrow = cursor.fetchone()
    conn.close()
    if dbrow and hash_password(password) == dbrow[1]:
        return True, dbrow[0]
    return False, None

class ProjectFrame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Management System")
        self.configure(bg='lightblue')

        # Set desired window size
        window_width = 1400
        window_height = 700

        # Get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Find the center point
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2) - 50

        # Set the geometry and center the window
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Set minimum size so it doesn't get too small
        self.minsize(1200, 600)
        self.state('zoomed')  # Start maximized
        self.frames = {}
        self.setup_frames()
        self.show_frame("HomePage")

    def setup_frames(self):
        self.frames["LoginPage"] = LoginPage(self, self)
        # Add more frames here as needed, e.g.:
        for frame in self.frames.values():
            frame.place(relwidth=1, relheight=1)
 
    def show_frame(self, name, role = None, user_id = None):
        for frame in self.frames.values():
            frame.place_forget()
        if name == "HomePage":
            # Recreate HomePage with the correct role
            if "HomePage" in self.frames:
                self.frames["HomePage"].destroy()
            self.frames["HomePage"] = HomePage(self, self, role, user_id)
        self.frames[name].place(relwidth=1, relheight=1)

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='lightblue')
        self.controller = controller

        # Configure grid
        for r in range(7):
            self.grid_rowconfigure(r, weight=1)
            for c in range(3):
                self.grid_columnconfigure(c, weight=1)

        # grid layout for the frame
        for r in range(7):  
            for c in range(3):  
                cell = tk.Frame(self, bg = 'lightblue',bd=1, relief="solid")
                cell.grid(row=r, column=c, sticky="nsew")

        # Title Label
        titlelabel = tk.Label(self, text="(Gas station name) Inventory Management System", font=("Arial", 24), bg='blue')
        titlelabel.grid(row=1, column=1, pady=(10, 5), sticky="")

        # Picture logo
        img = Image.open("images/loginpicture.png")
        img = img.resize((200, 200)) 
        logo = ImageTk.PhotoImage(img)
        logolabel = tk.Label(self, image=logo, bg='lightblue')
        logolabel.image = logo 
        logolabel.grid(row=2, column=1, pady=(5, 10))

        # Username
        username_frame = tk.Frame(self, bg='lightblue')
        username_label = tk.Label(username_frame, text="Username:", font=("Arial", 14), bg='lightblue')
        username_label.pack(side="left", padx=(0, 10))
        self.usernametextbox = tk.Entry(username_frame, width=30, font=("Arial", 14), bg='white')
        self.usernametextbox.pack(side="left")
        self.usernametextbox.focus_set() 
        username_frame.grid(row=3, column=1, pady=5, sticky="")

        # Password
        password_frame = tk.Frame(self, bg='lightblue')
        password_label = tk.Label(password_frame, text="Password:", font=("Arial", 14), bg='lightblue')
        password_label.pack(side="left", padx=(0, 10))
        self.passwordtextbox = tk.Entry(password_frame, show='*', width=30, font=("Arial", 14), bg='white')
        self.passwordtextbox.pack(side="left")
        password_frame.grid(row=4, column=1, pady=5, sticky="")

        # Login button
        loginbutton = tk.Button(self, text="Login", font=("Arial", 14), bg='green', fg='white', command=self.Onclick)
        loginbutton.grid(row=5, column=1, pady=10)

        # QOL Bindings
        self.usernametextbox.bind("<Return>", lambda e: self.passwordtextbox.focus_set())
        self.usernametextbox.bind("<Down>", lambda e: self.passwordtextbox.focus_set())
        self.passwordtextbox.bind("<Up>", lambda e: self.usernametextbox.focus_set())
        self.passwordtextbox.bind("<Return>", lambda e: self.Onclick())
        loginbutton.bind("<Up>", lambda e: self.passwordtextbox.focus_set())
        self.controller = controller

    def Onclick(self):
        username = self.usernametextbox.get()
        password = self.passwordtextbox.get()
        success, user_id= check_login(username, password)
        if success:
            if user_id== 1:
                role = "admin"
            else:
                role = "user"
            messagebox.showinfo(f"Access granted!!",f"Welcome, {username}!")
            self.controller.show_frame("HomePage", role = role, user_id = user_id)  # Example: switch to another frame
        else:
            messagebox.showerror("Access denied", "Invalid username or password.")
        self.usernametextbox.delete(0, tk.END)
        self.passwordtextbox.delete(0, tk.END)
        self.usernametextbox.focus_set()

class HomePage(tk.Frame):
    def __init__(self, parent, controller, role, user_id):
        self.shift_icon = ImageTk.PhotoImage(Image.open("images/shift.png").resize((24, 24)))
        self.income_icon = ImageTk.PhotoImage(Image.open("images/income.png").resize((24, 24)))
        self.price_icon = ImageTk.PhotoImage(Image.open("images/price.png").resize((24, 24)))
        self.delivery_icon = ImageTk.PhotoImage(Image.open("images/delivery.png").resize((24, 24)))
        self.inventory_icon = ImageTk.PhotoImage(Image.open("images/inventory.png").resize((24, 24)))
        self.transactions_icon = ImageTk.PhotoImage(Image.open("images/transaction.png").resize((24, 24)))
        self.logout_icon = ImageTk.PhotoImage(Image.open("images/logout.png").resize((24, 24)))
        #buttons setup
        self.buttons = [
            ("Start Shift", self.shift_icon, lambda: self.Onclick(1)),
            ("Income", self.income_icon, lambda: self.Onclick(2)),
            ("Price", self.price_icon, lambda: self.Onclick(3)),  # Assuming price is part of income
            ("Delivery", self.delivery_icon, lambda: self.Onclick(4)),
            ("Inventory", self.inventory_icon, lambda: self.Onclick(5)),
            ("Transactions", self.transactions_icon, lambda: self.Onclick(6)),
            ("Logout", self.logout_icon, lambda: self.Onclick(7))
        ]
        
        super().__init__(parent, bg='lightblue')
        self.role = role
        self.user_id = user_id
        self.controller = controller
        self.shift_started = False
        self.shift_button = None

        # grid layout for the frame
        for r in range(2):
            for c in range(1):
                cell = tk.Frame(self, bg='lightblue', bd=1, relief="solid")
                cell.grid(row=r, column=c, sticky="nsew")

        # Configure grid
        for r in range(2):
            self.grid_rowconfigure(r, weight=0)
            w = 0
            for c in range(1):
                self.grid_columnconfigure(c, weight=w)
                w += 1

        # Navigation bar
        
        if self.role == "admin":
            self.admin_navbar()
        else:
            self.user_navbar()
            self.user_id = 2

        # Main content area (container)
        self.main_content = tk.Frame(self, bg='white')
        self.main_content.grid(row=1, column=0, sticky='nsew')
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.current_page = None

        self.show_content(DefaultPage, userlogin = False)  

    def admin_navbar(self):
        nav_frame = tk.Frame(self, bg='gray')
        nav_frame.grid(row=0, column=0, sticky='ew')
        for text, icon, cmd in self.buttons:
            if text == "Start Shift":
                self.shift_button = tk.Button(nav_frame, text=text, image=icon, compound='left', relief= 'raised', bd = 4, command=cmd)
                self.shift_button.pack(side='left', padx=5, pady=5)
            else:
                tk.Button(nav_frame, text=text, image=icon, compound='left',  relief= 'raised', bd = 4, command=cmd).pack(side='left', padx=5, pady=5)
            
    def toggle_shift(self):
        timenow = datetime.datetime.now().strftime("%I:%M:%S:%p")
        shift_date = datetime.datetime.now().strftime("%Y-%m-%d")
        shift_type = datetime.datetime.now().strftime("%p")
        user_id = self.user_id
        conn = sqlite3.connect('Databases/inventory_db.db')
        cursor = conn.cursor()
        
        if not self.shift_started:
            cursor.execute('''INSERT INTO shift(user_id, shift_date, shift_type, shift_start_time) 
                VALUES (?, ?, ?, ?)''',(user_id, shift_date, shift_type, timenow))
            conn.commit()  
            messagebox.showinfo("Start Shift", f"{shift_type} Shift started successfully at {timenow}")
            self.shift_button.config(text="End Shift")
            self.shift_started = True  
            self.show_content(DefaultPage, userlogin = True)
            
        else:
            cursor.execute('SELECT shift_id FROM shift WHERE user_id = ? AND shift_end_time IS NULL ORDER BY shift_id DESC LIMIT 1', (user_id,))
            row = cursor.fetchone()
            if row:
                shift_id = row[0]
                cursor.execute('UPDATE shift SET shift_end_time = ? WHERE shift_id = ?', (timenow, shift_id))
                conn.commit()
            messagebox.showinfo("End shift",f"{shift_type} Shift ended at {timenow}")
            self.shift_button.config(text="Start Shift")
            self.shift_started = False
            self.show_content(DefaultPage, userlogin = False)
            
        conn.close()

    def user_navbar(self):
        nav_frame = tk.Frame(self, bg='gray')
        nav_frame.grid(row=0, column=0, sticky='ew')
        for text, icon, cmd in self.buttons:
            if text == "Start Shift":
                self.shift_button = tk.Button(nav_frame, text=text, image=icon, compound='left', relief= 'raised', bd = 4, command=cmd)
                self.shift_button.pack(side='left', padx=5, pady=5)
            elif text == "Logout":
                tk.Button(nav_frame, text=text, image=icon, compound='left', relief= 'raised', bd = 4, command=cmd).pack(side='left', padx=5, pady=5)
        
    def Onclick(self, number):
        def income_report(time_period):
            messagebox.showinfo("Income Report", "Income report generated successfully!")
            self.show_content(DashboardPage)
        match number:
            case 1:
                self.toggle_shift()
            case 2:
                menu = tk.Menu(self, tearoff=0)
                menu.add_command(label="Daily income", command=lambda: income_report("Daily"))
                menu.add_command(label="Weekly income", command=lambda: income_report("Weekly"))
                menu.add_command(label="Monthly income", command=lambda: income_report("Monthly"))
                menu.add_command(label="Yearly income", command=lambda: income_report("Yearly"))
                menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
            case 3: 
                print("Price button clicked")
            case 4:
                self.show_content(DeliveryPage) 
                
            case 5:
                self.show_content(InventoryPage)
                
            case 6:
                self.show_content(TransactionsPage)
            case 7:
                if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
                    self.controller.show_frame("LoginPage")  
                    
    def show_content(self, PageClass, *args, **kwargs):
        if self.current_page:
            self.current_page.destroy()
        if PageClass == DefaultPage:
            kwargs['user_id'] = self.user_id
        self.current_page = PageClass(self.main_content, *args, **kwargs)
        self.current_page.pack(fill='both', expand=True)
        
class DefaultPage(tk.Frame):
    def __init__(self, parent, userlogin = False, user_id = None):
        super().__init__(parent, bg='white')

        self.userlogin = userlogin
        self.user_id = user_id
        for r in range(3):
            self.grid_rowconfigure(r, weight=1, minsize=100)
            for c in range(3):
                self.grid_columnconfigure(c, weight=1, minsize=100)
                cell = tk.Frame(self, bg="#91C4EE", bd=1, relief="solid")
                cell.grid(row=r, column=c, sticky="nsew")

        # Container frame on lower right corner
        bottom_right = tk.Frame(self, bg='white', width=50)
        bottom_right.grid(row=2, column=2, sticky="se", padx=10, pady=10)
        bottom_right.grid_propagate(False)  

        # Stack the labels inside the container frame
        self.last_logout_label = tk.Label(bottom_right, font=("Comic Sans MS", 16), bg='white')
        self.last_logout_label.pack(anchor="e")
        self.date_label = tk.Label(bottom_right, font=("Comic Sans MS", 16), bg='white')
        self.date_label.pack(anchor="e")
        self.clock_label = tk.Label(bottom_right, font=("Comic Sans MS", 16), bg='white')
        self.clock_label.pack(anchor="e")
        self.updateclock()
        
        
    def updateclock(self):
        conn = sqlite3.connect('Databases/inventory_db.db')
        cursor = conn.cursor()
        monthnow = datetime.datetime.now().strftime("%B")
        weeknow = datetime.datetime.now().strftime("%A")
        daynow = datetime.datetime.now().strftime("%d")
        yearnow = datetime.datetime.now().strftime("%Y")
        timenow = datetime.datetime.now().strftime("%I:%M:%S %p")
        self.date_label.config(text=f"Current Date: {weeknow}, {monthnow} {daynow}, {yearnow}")  
        self.clock_label.config(text = f"Current Time: {timenow}") 
        last_logout_date = "N/A"
        last_logout_time = "N/A"
        cursor.execute("SELECT shift_id FROM shift WHERE shift_end_time IS NOT NULL ORDER BY shift_id DESC LIMIT 1")
        row = cursor.fetchone()
        last_logout = "N/A"
        if row:
            latest_shift_id = row[0]
            # Now get the shift_end_time for that shift_id
            cursor.execute("SELECT shift_end_time, shift_date FROM shift WHERE shift_id = ?", (latest_shift_id,))
            row2 = cursor.fetchone()
            
            if row2 and row2[0]:
                try:
                    lasttime = datetime.datetime.strptime(row2[0], "%I:%M:%S:%p")
                    lastdate = datetime.datetime.strptime(row2[1], "%Y-%m-%d")
                    last_logout_date = lastdate.strftime("%A, %B %d, %Y")
                    last_logout_time = lasttime.strftime("%I:%M:%S %p")
                except Exception as e:
                    last_logout_time = str(row2[0])
                    last_logout_date = str(row2[1])
                    print("Error", e)
        self.last_logout_label.config(text=f"Last Shift: {last_logout_date} at {last_logout_time}")
        conn.close()
        if self.userlogin:
            self.last_logout_label.config(text="")
            self.after(1000, self.updateclock)
            
            
        
                
class DeliveryPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='white')
        tk.Label(self, text="Delivery Content").pack()
        
class DashboardPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='white')
        tk.Label(self, text="Dashboard Content").pack()

class InventoryPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='white')
        tk.Label(self, text="Inventory Content").pack()

class TransactionsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='white')
        # Main content area with a scrollable table

        # Example: Scrollable table using ttk.Treeview
        columns = ('Pump number', 'Fuel_type', 'Volume', 'Price', 'Date')
        tree = ttk.Treeview(self, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center', width=100)
        tree.pack(side='left', fill='both', expand=True)

        # Add vertical scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Example data
        connect = sqlite3.connect('Databases/inventory_db.db')
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM transactions')
        rows = cursor.fetchall()
        connect.close()
        for values in rows:
            tree.insert('', 'end', values=values)

# --- Main program ---
setup_database()
projectframe = ProjectFrame()
projectframe.mainloop()