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
            FOREIGN KEY (shift_id) REFERENCES shift(shift_id),
            FOREIGN KEY (pump_id) REFERENCES pump(pump_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price(
        price_id INTEGER PRIMARY KEY AUTOINCREMENT,
        pump_id INTEGER NOT NULL,
        price INTEGER NOT NULL, 
        effective_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (pump_id) REFERENCES pump(pump_id)
        )
        '''
    )
    
    # Set the fuel types
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
        self.shift_started = False
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle close event
        self.minsize(1200, 600)
        self.state('zoomed')  # Start maximized
        self.frames = {}
        self.setup_frames()
        self.show_frame("LoginPage")

    # Placing Pages(Loginpage, Homepage)
    def setup_frames(self):
        self.frames["LoginPage"] = LoginPage(self, self)
        for frame in self.frames.values():
            frame.place(relwidth=1, relheight=1)
 
    def show_frame(self, name, role = None, user_id = None):
        for frame in self.frames.values():
            frame.place_forget()
            
            #if hasattr(frame, 'unbind_enter'):
            #   frame.unbind_enter()
            
        if name == "HomePage":
            if "HomePage" in self.frames:
                self.frames["HomePage"].destroy()
            self.frames["HomePage"] = HomePage(self, self, role, user_id)
        self.frames[name].place(relwidth=1, relheight=1)
        self.homepage = self.frames.get("HomePage")
        if name == "LoginPage":
            self.frames[name].bind_enter()
        
    # Error message when shift is active
    def on_closing(self):
        if self.shift_started:
            messagebox.showwarning("Action Blocked", "You cannot exit the program while logged in. Please logout first.")
            self.homepage.show_content(DefaultPage, userlogin = True)
        else:
            self.destroy()

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Modern color scheme
        self.login_icon = ImageTk.PhotoImage(Image.open("images/login.png").resize((108, 108)))
        self.bg_color = '#2c3e50'  # Dark blue
        self.primary_color = '#3498db'  # Bright blue
        self.secondary_color = '#2980b9'  # Darker blue
        self.accent_color = '#e74c3c'  # Red for errors
        self.light_text = '#ecf0f1'  # Light gray
        self.dark_text = '#2c3e50'   # Dark blue
        self.entry_bg = '#ffffff'    # White
        
        # Configure the frame
        self.configure(bg=self.bg_color)
        
        # Create a main container frame
        container = tk.Frame(self, bg=self.bg_color)
        container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Create a card-like frame for the login form
        login_card = tk.Frame(container, bg=self.light_text, bd=0, 
                             highlightbackground=self.primary_color, 
                             highlightthickness=0, 
                             relief='raised')
        login_card.pack(expand=True, fill='both', padx=(0, 0), pady=(0, 0))
        
        # Configure grid for the card
        login_card.grid_rowconfigure(0, weight=1)
        login_card.grid_rowconfigure(1, weight=0)
        login_card.grid_rowconfigure(2, weight=0)
        login_card.grid_rowconfigure(3, weight=0)
        login_card.grid_rowconfigure(4, weight=0)
        login_card.grid_rowconfigure(5, weight=0)
        login_card.grid_rowconfigure(6, weight=1)
        login_card.grid_columnconfigure(0, weight=1)
        login_card.grid_columnconfigure(1, weight=0)
        login_card.grid_columnconfigure(2, weight=1)
        
        # Header section
        header_frame = tk.Frame(login_card, bg=self.primary_color)
        header_frame.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=0, pady=0)
        
        # Title in header
        title_label = tk.Label(
            header_frame, 
            text="Dwyane's Inventory System", 
            font=("Segoe UI", 24, "bold"), 
            bg=self.primary_color, 
            fg=self.light_text,
            pady=20
        )
        title_label.pack(fill='x', expand=True)
        
        # Logo 
        logo_label = tk.Label(
            login_card, 
            image= self.login_icon, 
            font=("Arial", 72), 
            bg=self.light_text, 
            fg=self.primary_color
        )
        logo_label.grid(row=1, column=1, pady=(30, 10))
        
        # Subtitle
        subtitle = tk.Label(
            login_card,
            text="Secure Access to Your Inventory",
            font=("Segoe UI", 12),
            bg=self.light_text,
            fg=self.dark_text
        )
        subtitle.grid(row=2, column=1, pady=(0, 30))
        
        # Username section
        username_frame = tk.Frame(login_card, bg=self.light_text)
        username_frame.grid(row=3, column=1, sticky='ew', pady=5)
        
        # Username label with icon
        tk.Label(
            username_frame, 
            text="👤 Username", 
            font=("Segoe UI", 11), 
            bg=self.light_text, 
            fg=self.dark_text,
            anchor='w'
        ).pack(fill='x', padx=5)
        
        # Modern entry field
        self.usernametextbox = ttk.Entry(
            username_frame, 
            width=30, 
            font=("Segoe UI", 12)
        )
        self.usernametextbox.pack(fill='x', pady=5, padx=5, ipady=8)
        self.usernametextbox.focus_set()
        
        # Password section
        password_frame = tk.Frame(login_card, bg=self.light_text)
        password_frame.grid(row=4, column=1, sticky='ew', pady=5)
        
        #password label
        tk.Label(
            password_frame, 
            text="🔒 Password", 
            font=("Segoe UI", 11), 
            bg=self.light_text, 
            fg=self.dark_text,
            anchor='w'
        ).pack(fill='x', padx=5)
        
        #password textbox
        self.passwordtextbox = ttk.Entry(
            password_frame, 
            show='*', 
            width=30, 
            font=("Segoe UI", 12)
        )
        self.passwordtextbox.pack(fill='x', pady=5, padx=5, ipady=8)
        
        # Login button with modern styling
        login_btn = tk.Button(
            login_card,
            text="LOGIN",
            font=("Segoe UI", 12, "bold"),
            bg=self.primary_color,
            fg=self.light_text,
            bd=0,
            padx=30,
            pady=10,
            cursor="hand2",
            command=self.Onclick,
            activebackground=self.secondary_color,
            activeforeground=self.light_text
        )
        login_btn.grid(row=5, column=1, pady=(20, 10), sticky='ew')
        
        # Status message label (hidden by default)
        self.status_label = tk.Label(
            login_card,
            text="",
            font=("Segoe UI", 10),
            bg=self.light_text,
            fg=self.accent_color
        )
        self.status_label.grid(row=6, column=1, pady=(5, 20))
        
        # Footer
        footer = tk.Label(
            login_card,
            text="© 2023 Dwyane's Inventory Management System",
            font=("Segoe UI", 9),
            bg=self.light_text,
            fg='#7f8c8d'
        )
        footer.grid(row=7, column=1, pady=(10, 20))
        
        # QOL Bindings (preserved from original)
        self.usernametextbox.bind("<Return>", lambda e: self.passwordtextbox.focus_set())
        self.usernametextbox.bind("<Down>", lambda e: self.passwordtextbox.focus_set())
        self.passwordtextbox.bind("<Up>", lambda e: self.usernametextbox.focus_set())
        login_btn.bind("<Up>", lambda e: self.passwordtextbox.focus_set())
         
    def bind_enter(self):
        self.passwordtextbox.bind("<Return>", lambda e: self.Onclick())

    def unbind_enter(self):
        self.unbind_all("<Return>")

    # Method to handle login button click
    def Onclick(self):
        self.passwordtextbox.unbind("<Return>")
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
        self.login_icon = ImageTk.PhotoImage(Image.open("images/login.png").resize((36, 36)))
        
        #navigation buttons 
        self.buttons = [
            ("Start Shift", self.shift_icon, lambda: self.Onclick(1)),
            ("Income", self.income_icon, lambda: self.Onclick(2)),
            ("Price", self.price_icon, lambda: self.Onclick(3)),
            ("Delivery", self.delivery_icon, lambda: self.Onclick(4)),
            ("Inventory", self.inventory_icon, lambda: self.Onclick(5)),
            ("Transactions", self.transactions_icon, lambda: self.Onclick(6)),
            ("Logout", self.logout_icon, lambda: self.Onclick(7))
        ]

        super().__init__(parent, bg='#f5f7fa')  # Match login background
        self.role = role
        self.user_id = user_id
        self.controller = controller
        self.shift_button = None
        self.shift_started = self.controller.shift_started

        # Configure grid
        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1)   
        self.grid_columnconfigure(0, weight=1)

        # Navigation bar
        nav_frame = tk.Frame(self, bg='#2c3e50', height=70) 
        nav_frame.grid(row=0, column=0, sticky='ew')
        nav_frame.grid_propagate(False)  
        
        # Logo frame for navigation bar
        logo_frame = tk.Frame(nav_frame, bg="#2c3e50")
        logo_frame.pack(side='left', padx=20)
        
        # Designs at the left side of the navbar 
        logo_label = tk.Label(
            logo_frame, 
            image = self.login_icon, 
            font=("Arial", 24), 
            bg='#2c3e50', 
            fg='#ecf0f1'
        )
        logo_label.pack(side='left', padx=(0, 10))
        
        title_label = tk.Label(
            logo_frame, 
            text="Dwyane's Inventory", 
            font=("Segoe UI", 16, "bold"), 
            bg='#2c3e50', 
            fg='#ecf0f1'
        )
        title_label.pack(side='left')

        # Create container for nav buttons
        button_frame = tk.Frame(nav_frame, bg='#2c3e50')
        button_frame.pack(side='right', padx=20)
        
        # Create buttons based on role
        self.navbar(button_frame) 

        # Main content area - modern card design
        self.main_content = tk.Frame(self, bg="#ffffff", bd=0, highlightthickness=0)
        self.main_content.grid(row=1, column=0, sticky='nsew', padx=20, pady=20)
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.current_page = None

        # Shadow effect of the maincontent area
        shadow = tk.Frame(self, bg="#b5b7bb", bd=0)
        shadow.place(in_=self.main_content, relx=0, rely=0, x=-4, y=-4, relwidth=1, relheight=1, width=8, height=8)
        self.main_content.lift() 
        
        self.show_content(DefaultPage, userlogin = False)

    # Admin navigation bar method
    def navbar(self, parent_frame):
        # Create modern styled buttons for user role without changing names
        for text, icon, cmd in self.buttons:
            if self.role == "user" and text not in ["Start Shift", "Logout"]:
                continue
            button_frame = tk.Frame(parent_frame, bg='#2c3e50', padx=5)
            button_frame.pack(side='left', padx=5)
            # Button design
            button = tk.Button(
                    button_frame,
                    text=text,
                    image=icon,
                    compound='left',
                    bg='#3498db' if text != "Logout" else '#e74c3c',
                    fg='white',
                    font=("Segoe UI", 10, "bold"),
                    bd=4,
                    padx=10,
                    pady=8,
                    relief='raised',
                    command=cmd,
                    cursor="hand2",
                    activebackground='#2980b9' if text != "Logout" else '#c0392b',
                    height = 6,  # Set fixed height in text lines
                )
            button.pack() 
               
            # Store reference to shift button
            if text == "Start Shift":
                    self.shift_button = button            
                
    # When Start Shift button is clicked, it will toggle the shift status            
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
            self.controller.shift_started = True 
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
            self.controller.shift_started = False
            self.show_content(DefaultPage, userlogin = False)
        conn.close()
    
    # Method to handle button clicks 
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
                if self.controller.shift_started:
                    messagebox.showwarning("Action Blocked", "You cannot logout while a shift is active. Please end the shift first.")
                    self.show_content(DefaultPage, userlogin = True)
                else:
                    if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
                        self.controller.show_frame("LoginPage")  
    
    #method for switching frames when buttons are clicked                
    def show_content(self, PageClass, *args, **kwargs):
        if self.current_page:
            self.current_page.destroy()
        if PageClass == DefaultPage:
            kwargs['user_id'] = self.user_id
        self.current_page = PageClass(self.main_content, *args, **kwargs)
        self.current_page.pack(fill='both', expand=True)
        
class DefaultPage(tk.Frame):
    def __init__(self, parent, userlogin = False, user_id = None):
        super().__init__(parent, bg='#91C4EE')
        
        self.diesel1_icon = ImageTk.PhotoImage(Image.open("images/diesel_1.png").resize((48, 48)))
        self.diesel2_icon = ImageTk.PhotoImage(Image.open("images/diesel_2.png").resize((48, 48)))
        self.premium1_icon = ImageTk.PhotoImage(Image.open("images/premium_1.png").resize((48, 48)))
        self.premium2_icon = ImageTk.PhotoImage(Image.open("images/premium_2.png").resize((48, 48)))
        self.premium3_icon = ImageTk.PhotoImage(Image.open("images/premium_3.png").resize((48, 48)))
        self.unleaded_icon = ImageTk.PhotoImage(Image.open("images/unleaded.png").resize((48, 48)))
        
        self.userlogin = userlogin
        self.user_id = user_id
        
        self.dummy_focus = tk.Frame(self)
        self.dummy_focus.place(x=0, y=0, width=1, height=1)
        
        for r in range(3):
            self.grid_rowconfigure(r, weight=1, minsize=100)
            for c in range(3):
                self.grid_columnconfigure(c, weight=1, minsize=100)
                    
        # Container frame on top left square
        top_left = tk.Frame(self, bg="#91C4EE", bd = 2, relief= "solid",  width=50)
        top_left.grid(row = 0, column = 0, sticky="nsew", padx=10, pady=10)
        top_left.grid_propagate(False)

        # Container frame on top middle square
        top_middle = tk.Frame(self, bg="#91C4EE", bd = 2, relief = "solid", width=50)
        top_middle.grid(row = 0, column = 1, sticky="nsew", padx=10, pady=10)
        top_middle.grid_propagate(False)

        # Container frame on top right square
        top_right = tk.Frame(self, bg="#91C4EE",  bd = 2, relief = "solid",width=50)
        top_right.grid(row = 0, column = 2, sticky="nsew", padx=10, pady=10)
        top_right.grid_propagate(False)
        
        # Container frame on middle left square
        middle_left = tk.Frame(self, bg="#91C4EE" , bd = 2 , relief="solid",  width=50)
        middle_left.grid(row = 1, column = 0, sticky="nsew", padx=10, pady=10)
        middle_left.grid_propagate(False)

        # Container frame on middle middle square
        middle_middle = tk.Frame(self, bg="#91C4EE" , bd = 2 , relief="solid",  width=50)
        middle_middle.grid(row = 1, column = 1, sticky="nsew", padx=10, pady=10)
        middle_middle.grid_propagate(False)

        # Container frame on middle right square
        middle_right = tk.Frame(self, bg="#91C4EE" , bd = 2 , relief="solid",  width=50)
        middle_right.grid(row = 1, column = 2, sticky="nsew", padx=10, pady=10)
        middle_right.grid_propagate(False)
        
        #widget list
        self.widget_configs = [
        ("diesel1_button", top_left, self.diesel1_icon, "Diesel 1", 1, "diesel1_volume_textbox", "diesel1_price_textbox", "Diesel 1 Volume:"),
        ("diesel2_button", top_middle, self.diesel2_icon, "Diesel 2", 2, "diesel2_volume_textbox","diesel2_price_textbox", "Diesel 2 Volume:"),
        ("premium1_button", top_right, self.premium1_icon, "Premium 1", 3,"premium1_volume_textbox","premium1_price_textbox", "Premium 1 Volume:"),
        ("premium2_button", middle_left, self.premium2_icon, "Premium 2", 4, "premium2_volume_textbox", "premium2_price_textbox", "Premium 2 Volume:"),
        ("premium3_button", middle_middle, self.premium3_icon, "Premium 3", 5,"premium3_volume_textbox", "premium3_price_textbox", "Premium 3 Volume:"),
        ("unleaded_button", middle_right, self.unleaded_icon, "Unleaded", 6,"unleaded_volume_textbox", "unleaded_price_textbox", "Unleaded Volume:"),
    ]
        # Create buttons dynamically based on the button_configs
        for button_name, gridposition, icon, text, cmd_num, volume_textbox, price_texbox, volume_label in self.widget_configs:
            button = tk.Button(
                    gridposition,
                    text=text,
                    image= icon,
                    compound='left',
                    bg="#70818c", 
                    fg='white',
                    font=("Segoe UI", 10, "bold"),
                    bd=4,
                    padx=10,
                    pady=5,
                    relief='raised',
                    command=lambda n = cmd_num: self.Onclick(n),
                    cursor="hand2",
                    activebackground="#4f5a62",
                    state = "disabled",
                    width = 150,
                    height = 30 
            )
            button.pack(anchor='center', padx=10, pady=5)
            volume_label = tk.Label(gridposition, text= volume_label ,font=("Comic Sans MS", 14), bg = "#91C4EE")
            volume_label.pack(anchor = 'center', padx = 10, pady = 5)
            volumetxbx = ttk.Entry(
            gridposition, 
            width=20, 
            font=("Comic Sans MS", 12),
            state = "disabled"
            )
            volumetxbx.bind("<Return>", lambda e: self.submit())
            volumetxbx.pack(anchor='center', padx= 10, pady= 5)
            price_label =tk.Label(gridposition, text= "Price:",font=("Comic Sans MS", 14), bg = "#91C4EE")
            price_label.pack(anchor = 'center', padx = 10, pady = 5)
            price_txbx = ttk.Entry(
            gridposition, 
            width=20, 
            font=("Comic Sans MS", 12),
            state= "disabled"
            )
            price_txbx.pack(anchor='center', padx= 10, pady= 5)
            setattr(self, button_name, button)
            setattr(self, volume_textbox, volumetxbx)
            getattr(self, volume_textbox).bind('<KeyRelease>', lambda e, n=cmd_num: self.update_price(n))
            setattr(self, price_texbox, price_txbx)
            
        # Container frame on bottom left square
        bottom_left = tk.Frame(self, bg="#91C4EE" , bd = 2 , relief="solid",  width=50)
        bottom_left.grid(row = 2, column = 0, sticky="nsew", padx=10, pady=10)
        bottom_left.grid_propagate(False)
        
        clear_button = tk.Button(bottom_left,
                    text="Clear",
                    bg="#DD1F1F", 
                    fg='white',
                    font=("Segoe UI", 10, "bold"),
                    bd=4,
                    padx=10,
                    pady=5,
                    relief='raised',
                    command=lambda: self.clear(),
                    cursor="hand2",
                    activebackground="#F10A0A",
                    width = 15,
                    height = 2 
        )
        clear_button.pack(anchor='center', padx=10, pady=20)

        # Container frame on bottom middle square
        bottom_middle = tk.Frame(self, bg="#91C4EE" , bd = 2 , relief="solid",  width=50)
        bottom_middle.grid(row = 2, column = 1, sticky="nsew", padx=10, pady=10)
        bottom_middle.grid_propagate(False)
        
        submit_button = tk.Button(bottom_middle,
                    text="Submit",
                    bg="#0EAF0E", 
                    fg='white',
                    font=("Segoe UI", 10, "bold"),
                    bd=4,
                    padx=10,
                    pady=5,
                    relief='raised',
                    command=lambda: self.submit(),
                    cursor="hand2",
                    activebackground="#0A820A",
                    width = 15,
                    height = 2 
        )
        submit_button.pack(anchor='center', padx=10, pady = 20)
        
        # Container frame on lower right square
        bottom_right = tk.Frame(self, bg="#91C4EE" , bd = 2 , relief="solid",  width=50)
        bottom_right.grid(row=2, column=2, sticky="nsew", padx=10, pady=10)
        bottom_right.grid_propagate(False)  

        # Stack the labels inside the container frame
        self.clock_label = tk.Label(bottom_right, font=("Comic Sans MS", 14), bg="#91C4EE", anchor='e', justify='right')
        self.clock_label.pack(side='bottom', anchor='e', padx=10, pady=(0,2), fill='x')        
        self.date_label = tk.Label(bottom_right, font=("Comic Sans MS", 14), bg="#91C4EE", anchor='e', justify='right')
        self.date_label.pack(side='bottom', anchor='e', padx=10, pady=(0,2), fill='x')
        self.last_logout_label = tk.Label(bottom_right, font=("Comic Sans MS", 14), bg="#91C4EE", anchor='e', justify='right')
        self.last_logout_label.pack(side='bottom', anchor='e', padx=10, pady=(0,2), fill='x')
        self.updateclock()  
        self.bind_all("<Button-1>", self.remove_focus)
        
        # state of the widgets based if the user has pressed the shift button
        if self.userlogin: 
            # enabling the buttons when the user has pressed start shift
            for widget in self.widget_configs:
                getattr(self, widget[0]).config(state = "normal")
            
            #Clearing the textboxes when the user has pressed start shift    
            for textbox in self.widget_configs:
                getattr(self, textbox[5]).delete(0,tk.END)
                getattr(self, textbox[6]).delete(0,tk.END)
        
        else:
            # disabling the buttons when the user has pressed ennd shift
            for widget in self.widget_configs:
                getattr(self, widget[0]).config(state = "disabled")
                getattr(self, widget[5]).config(state = "disabled")
            
            #Clearing the textboxes when the user has pressed end shift    
            for textbox in self.widget_configs:
                getattr(self, textbox[5]).delete(0,tk.END)
                getattr(self, textbox[6]).delete(0,tk.END)
    
    #This method calculates the price based on the volume entered in the corresponding textbox
    def update_price(self, number):
        match number:
            case 1:
                try:
                    volume = float(self.diesel1_volume_textbox.get())
                    price = volume *50
                    price_str = f"{price:.2f}"
                except ValueError:
                    price_str = ""
                self.diesel1_price_textbox.config(state="normal")
                self.diesel1_price_textbox.delete(0, tk.END)
                self.diesel1_price_textbox.insert(0, price_str)
                self.diesel1_price_textbox.config(state="disabled")
            case 2:
                try:
                    volume = float(self.diesel2_volume_textbox.get())
                    price = volume *50
                    price_str = f"{price:.2f}"
                except ValueError:
                    price_str = ""
                self.diesel2_price_textbox.config(state="normal")
                self.diesel2_price_textbox.delete(0, tk.END)
                self.diesel2_price_textbox.insert(0, price_str)
                self.diesel2_price_textbox.config(state="disabled") 
            case 3:
                try:
                    volume = float(self.premium1_volume_textbox.get())
                    price = volume *50
                    price_str = f"{price:.2f}"
                except ValueError:
                    price_str = ""
                self.premium1_price_textbox.config(state="normal")
                self.premium1_price_textbox.delete(0, tk.END)
                self.premium1_price_textbox.insert(0, price_str)
                self.premium1_price_textbox.config(state="disabled")  
            case 4:
                try:
                    volume = float(self.premium2_volume_textbox.get())
                    price = volume *50
                    price_str = f"{price:.2f}"
                except ValueError:
                    price_str = ""
                self.premium2_price_textbox.config(state="normal")
                self.premium2_price_textbox.delete(0, tk.END)
                self.premium2_price_textbox.insert(0, price_str)
                self.premium2_price_textbox.config(state="disabled")  
            case 5:
                try:
                    volume = float(self.premium3_volume_textbox.get())
                    price = volume *50
                    price_str = f"{price:.2f}"
                except ValueError:
                    price_str = ""
                self.premium3_price_textbox.config(state="normal")
                self.premium3_price_textbox.delete(0, tk.END)
                self.premium3_price_textbox.insert(0, price_str)
                self.premium3_price_textbox.config(state="disabled")
            case 6:
                try:
                    volume = float(self.unleaded_volume_textbox.get())
                    price = volume *50
                    price_str = f"{price:.2f}"
                except ValueError:
                    price_str = ""
                self.unleaded_price_textbox.config(state="normal")
                self.unleaded_price_textbox.delete(0, tk.END)
                self.unleaded_price_textbox.insert(0, price_str)
                self.unleaded_price_textbox.config(state="disabled")    
    
    # Method to handle transaction submissions       
    def submit(self):
        answer = messagebox.askokcancel("Transaction Confirmation", 
                            "Are you sure all the information entered is correct") 
        if answer:
            for config in self.widget_configs:
                volume_entry = getattr(self, config[5])
                price_entry = getattr(self, config[6])
                if str(volume_entry['state']) == 'normal':
                    volume_value = volume_entry.get()
                    price_value = price_entry.get()
                    print(f"Enabled: {config[3]}, Volume: {volume_value}, Price: {price_value}")
                    
                # You can now use volume_value and price_value as needed
            conn = sqlite3.connect('Databases/inventory_db.db')
            cursor = conn.cursor()
            
            messagebox.showinfo("Transaction Confirmation", "Transaction Recorded 😊")  
            self.clear()
    
    #Method to remove focus when a textbox is focused on
    def remove_focus(self, event):
        widget = event.widget
    # Only remove focus if click is NOT on an Entry
        if not isinstance(widget, ttk.Entry):
            self.dummy_focus.focus_set()
    
    # Method to clear all textboxes
    def clear(self):
        for textbox in self.widget_configs: 
            getattr(self, textbox[5]).delete(0,tk.END)
            getattr(self, textbox[6]).config(state="normal")
            getattr(self, textbox[6]).delete(0,tk.END) 
            getattr(self, textbox[6]).config(state="disabled")                 
    
    #Method to handle button clicks TBR      
    def Onclick(self, button_number):
        match button_number:
            case 1:
                print("Diesel 1 clicked")
                self.clear()
                self.diesel1_volume_textbox.config(state = "normal")
                self.diesel1_volume_textbox.focus_set()
            case 2:
                print("Diesel 2 clicked")
                self.clear()
                self.diesel2_volume_textbox.config(state = "normal")
                self.diesel2_volume_textbox.focus_set()
            case 3:
                print("Premium 1 clicked")
                self.clear()
                self.premium1_volume_textbox.config(state = "normal")
                self.premium1_volume_textbox.focus_set()
            case 4:
                print("Premium 2 clicked")
                self.clear()
                self.premium2_volume_textbox.config(state = "normal")
                self.premium2_volume_textbox.focus_set()
            case 5:
                print("Premium 3 clicked")
                self.clear()
                self.premium3_volume_textbox.config(state = "normal")
                self.premium3_volume_textbox.focus_set()
            case 6:
                print("Unleaded clicked")  
                self.clear()
                self.unleaded_volume_textbox.config(state = "normal")
                self.unleaded_volume_textbox.focus_set()
     
    #Bottom right corner clock and date label   
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