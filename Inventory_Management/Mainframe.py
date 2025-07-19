import tkinter as tk
from PIL import Image, ImageTk 
from tkinter import messagebox, simpledialog, ttk
import datetime
import sqlite3
import hashlib
from typing import Dict, Union, cast, Type, TypeVar, Any
T = TypeVar('T', bound=tk.Frame)

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def setup_database():
    datenow = datetime.datetime.now().strftime("%m-%d-%Y")
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
            Price REAL NOT NULL,
            Date DATETIME,
            FOREIGN KEY (shift_id) REFERENCES shift(shift_id),
            FOREIGN KEY (pump_id) REFERENCES pump(pump_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price(
        price_id INTEGER PRIMARY KEY AUTOINCREMENT,
        fuel_type_id INTEGER NOT NULL,
        Name Text Not NULL,
        price REAL NOT NULL, 
        effective_date DATETIME,
        FOREIGN KEY (fuel_type_id) REFERENCES fuel_type(fuel_type_id)
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
        
    #setup prices initally
    cursor.execute('SELECT COUNT(*) FROM price')
    if cursor.fetchone()[0] == 0:
        dieselprice = simpledialog.askfloat(
                "Set Diesel Price",
                "Enter price per liter of diesel:",
            )
        cursor.execute('INSERT INTO price(fuel_type_id, price, Name,effective_date) VALUES (?,?,?,?)', (1,dieselprice,'Diesel',datenow,))
        diesel100price = simpledialog.askfloat(
                "Set Diesel100 Price",
                "Enter price per 100 liters of diesel:",
            )
        cursor.execute('INSERT INTO price(fuel_type_id, price, Name,effective_date) VALUES (?,?,?,?)', (1,diesel100price,'Diesel100',datenow,))
        
        premiumprice = simpledialog.askfloat(
                "Set Premium Price",
                "Enter price per liter of premium:",
            )
        cursor.execute('INSERT INTO price(fuel_type_id, price, Name,effective_date) VALUES (?,?,?,?)', (2,premiumprice,'Premium',datenow,))
        premium100price = simpledialog.askfloat(
                "Set Premium100 Price",
                "Enter price per 100 liters of premium:",
            )
        cursor.execute('INSERT INTO price(fuel_type_id, price, Name,effective_date) VALUES (?,?,?,?)', (2,premium100price,'Premium100',datenow,))
        
        unleadedprice = simpledialog.askfloat(
                "Set Unleaded Price",
                "Enter price per liter of Unleaded:",
            )
        cursor.execute('INSERT INTO price(fuel_type_id, price, Name,effective_date) VALUES (?,?,?,?)', (3,unleadedprice,'Unleaded',datenow,))
        unleaded100price = simpledialog.askfloat(
                "Set Unleaded100 Price",
                "Enter price per 100 liters of Unleaded:",
            )
        cursor.execute('INSERT INTO price(fuel_type_id, price, Name,effective_date) VALUES (?,?,?,?)', (3,unleaded100price,'Unleaded100',datenow,))

    conn.commit()
    conn.close()

def check_login(username: str, password: str):
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
        self.frames: Dict[str, Union[LoginPage, HomePage]] = {}
        self.setup_frames()
        self.show_frame("LoginPage")

    # Placing Pages(Loginpage, Homepage)
    def setup_frames(self):
        self.frames["LoginPage"] = LoginPage(self, self)
        for frame in self.frames.values():
            frame.place(relwidth=1, relheight=1)
 
    def show_frame(self, name : str, role: str | None = None, user_id: int | None = None):
        for frame in self.frames.values():
            frame.place_forget()
                
        if name == "HomePage":
            if "HomePage" in self.frames:
                self.frames["HomePage"].destroy()
            self.frames["HomePage"] = HomePage(self, self, role, user_id)
        self.frames[name].place(relwidth=1, relheight=1)
        self.homepage = self.frames.get("HomePage")
        if name == "LoginPage":
            login_frame = cast(LoginPage, self.frames[name])
            login_frame.bind_enter()
        
    # Error message when shift is active
    def on_closing(self):
        if self.shift_started:
            messagebox.showwarning("Action Blocked", "You cannot exit the program while logged in. Please logout first.") # type: ignore
            self.homepage.show_content(DefaultPage, userlogin = True) # type: ignore
        else:
            self.destroy()

class LoginPage(tk.Frame):
    def __init__(self, parent: tk.Tk, controller: ProjectFrame):
        super().__init__(parent)
        self.controller = controller
        
        # Modern color scheme
        self.login_icon = ImageTk.PhotoImage(Image.open("images/login.png").resize((108, 108))) # type:ignore
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
            text="© 2025 Dwyane's Inventory Management System",
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
        username = self.usernametextbox.get()
        password = self.passwordtextbox.get()
        success, user_id= check_login(username, password)
        if success:
            if user_id== 1:
                role = "admin"
            else:
                role = "user"
            messagebox.showinfo(f"Access granted!!",f"Welcome, {username}!") #type: ignore
            self.unbind_enter()
            self.controller.show_frame("HomePage", role = role, user_id = user_id)  
        else:
            messagebox.showerror("Access denied", "Invalid username or password.") #type: ignore
        self.usernametextbox.delete(0, tk.END)
        self.passwordtextbox.delete(0, tk.END)
        self.usernametextbox.focus_set()

class HomePage(tk.Frame):
    def __init__(self, parent: tk.Tk, controller: ProjectFrame, role: str | None, user_id: int |None):
        
        self.shift_icon = ImageTk.PhotoImage(Image.open("images/shift.png").resize((24, 24)))#type: ignore
        self.price_icon = ImageTk.PhotoImage(Image.open("images/price.png").resize((24, 24)))#type: ignore
        self.delivery_icon = ImageTk.PhotoImage(Image.open("images/delivery.png").resize((24, 24)))#type: ignore
        self.inventory_icon = ImageTk.PhotoImage(Image.open("images/inventory.png").resize((24, 24)))#type: ignore
        self.transactions_icon = ImageTk.PhotoImage(Image.open("images/transaction.png").resize((24, 24)))#type: ignore
        self.logout_icon = ImageTk.PhotoImage(Image.open("images/logout.png").resize((24, 24)))#type: ignore
        self.login_icon = ImageTk.PhotoImage(Image.open("images/login.png").resize((36, 36)))#type: ignore
        
        #navigation buttons 
        self.buttons = [
            ("Start Shift", self.shift_icon, lambda: self.Onclick(1)),
            ("Price", self.price_icon, lambda: self.Onclick(2)),
            ("Inventory", self.inventory_icon, lambda: self.Onclick(3)),
            ("Transactions", self.transactions_icon, lambda: self.Onclick(4)),
            ("Delivery", self.delivery_icon, lambda: self.Onclick(5)),
            ("Logout", self.logout_icon, lambda: self.Onclick(6))
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
        self.main_content.lift()  # type: ignore
        
        self.show_content(DefaultPage, userlogin = False)

    # Admin navigation bar method
    def navbar(self, parent_frame: tk.Frame):
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
            messagebox.showinfo("Start Shift", f"{shift_type} Shift started successfully at {timenow}")#type: ignore
            getattr(self, "shift_button").config(text ="End Shift")
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
            messagebox.showinfo("End shift",f"{shift_type} Shift ended at {timenow}")#type: ignore
            getattr(self, "shift_button").config(text ="Start Shift")
            self.shift_started = False
            self.controller.shift_started = False
            self.show_content(DefaultPage, userlogin = False)
        conn.close()
    
    # Method to handle button clicks 
    def Onclick(self, number: int):
        match number:
            case 1:
                self.toggle_shift()
            case 2: 
                self.show_content(PricePage)
            case 3:
                self.show_content(InventoryPage)
            case 4:
                self.show_content(TransactionsPage)
            case 5:
                self.show_content(DeliveryPage) 
            case 6:
                if self.controller.shift_started:
                    messagebox.showwarning("Action Blocked", "You cannot logout while a shift is active. Please end the shift first.")#type: ignore
                    self.show_content(DefaultPage, userlogin = True)
                else:
                    if messagebox.askyesno("Logout", "Are you sure you want to logout?"): #type: ignore
                        self.controller.show_frame("LoginPage")  
            case _:
                pass
    
    #method for switching frames when buttons are clicked                
    def show_content(self, PageClass: Type[T], *args: Any, **kwargs: Any)-> None:
        if self.current_page:
            self.current_page.destroy()
        if PageClass == DefaultPage:
            kwargs['user_id'] = self.user_id
        self.current_page = PageClass(self.main_content, *args, **kwargs)
        self.current_page.pack(fill='both', expand=True)
        
class DefaultPage(tk.Frame):
    def __init__(self, parent: tk.Frame, userlogin: bool = False, user_id: int | None = None):
        super().__init__(parent, bg='#91C4EE')
        
        self.diesel1_icon = ImageTk.PhotoImage(Image.open("images/diesel_1.png").resize((48, 48)))#type: ignore
        self.diesel2_icon = ImageTk.PhotoImage(Image.open("images/diesel_2.png").resize((48, 48)))#type: ignore
        self.premium1_icon = ImageTk.PhotoImage(Image.open("images/premium_1.png").resize((48, 48)))#type: ignore
        self.premium2_icon = ImageTk.PhotoImage(Image.open("images/premium_2.png").resize((48, 48)))#type: ignore
        self.premium3_icon = ImageTk.PhotoImage(Image.open("images/premium_3.png").resize((48, 48)))#type: ignore
        self.unleaded_icon = ImageTk.PhotoImage(Image.open("images/unleaded.png").resize((48, 48)))#type: ignore
        
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
                    command=lambda n = cmd_num: self.Onclick(n, self.widget_configs[n-1][5]),
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
            getattr(self, volume_textbox).bind('<KeyRelease>', lambda e, n=cmd_num: self.update_price(n, self.widget_configs[n-1][5],self.widget_configs[n-1][6]))#type: ignore
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
    def update_price(self, number: int, volumeboxname: str, priceboxname: str):
        price_per_liter: float = 0
        conn = sqlite3.connect('Databases/inventory_db.db')
        cursor = conn.cursor()
        match number:
            case 1 | 2:
                try:
                    volume = float(getattr(self, volumeboxname).get())
                    cursor.execute('SELECT COUNT(*) FROM fuel_type')
                    if volume < 100:
                        cursor.execute('''
                               SELECT price from price 
                               WHERE fuel_type_id = ?
                               AND Name = ?
                               ORDER BY price_id DESC
                               LIMIT 1
                               ''',(1,"Diesel",))
                    else:
                        cursor.execute('''
                               SELECT price from price 
                               WHERE fuel_type_id = ?
                               AND Name = ?
                               ORDER BY price_id DESC
                               LIMIT 1
                               ''',(1,"Diesel100",))
                    price_row = cursor.fetchone()
                    price_per_liter = price_row[0]
                    price = volume *price_per_liter
                    price_str = f"{price:.2f}"
                except Exception as e: #type: ignore
                    price_str = ""
                self.clearbox(priceboxname, price_str)
            case 3 | 4 | 5:
                try:
                    volume = float(getattr(self, volumeboxname).get())
                    if volume < 100:
                        cursor.execute('''
                               SELECT price from price 
                               WHERE fuel_type_id = ?
                               AND Name = ?
                               ORDER BY price_id DESC
                               LIMIT 1
                               ''',(2,"Premium",))
                    else:
                        cursor.execute('''
                               SELECT price from price 
                               WHERE fuel_type_id = ?
                               AND Name = ?
                               ORDER BY price_id DESC
                               LIMIT 1
                               ''',(2,"Premium100",))
                    price_row = cursor.fetchone()
                    price_per_liter = price_row[0]
                    price = volume *price_per_liter
                    price_str = f"{price:.2f}"
                except Exception as e: #type: ignore
                    price_str = ""
                self.clearbox(priceboxname, price_str)
            case 6:
                try:
                    volume = float(getattr(self, volumeboxname).get())
                    if volume < 100:
                        cursor.execute('''
                               SELECT price from price 
                               WHERE fuel_type_id = ?
                               AND Name = ?
                               ORDER BY price_id DESC
                               LIMIT 1
                               ''',(3,"Unleaded",))
                    else:
                        cursor.execute('''
                               SELECT price from price 
                               WHERE fuel_type_id = ?
                               AND Name = ?
                               ORDER BY price_id DESC
                               LIMIT 1
                               ''',(3,"Unleaded100",))
                    price_row = cursor.fetchone()
                    price_per_liter = price_row[0]
                    price = volume *price_per_liter
                    price_str = f"{price:.2f}"
                except Exception as e: #type: ignore
                    price_str = ""
                self.clearbox(priceboxname, price_str)
            case _: pass
        conn.commit()
        conn.close()
    
    # Method to handle transaction submissions       
    def submit(self):
        for config in self.widget_configs:
            volume_entry = getattr(self, config[5])
            price_entry = getattr(self, config[6])
            datenow = datetime.datetime.now().strftime("%Y-%m-%d")
            if str(volume_entry['state']) == 'normal':
                #print(f"Transaction of: {config[3]}")
                try:
                    volume_value = float(getattr(self, config[5]).get())
                    price_value = price_entry.get()
                    answer = messagebox.askokcancel("Transaction Confirmation", #type: ignore
                            "Are you sure all the information entered is correct") 
                    if answer:
                        #print(f"Enabled: {config[3]}, Volume: {volume_value}, Price: {price_value}")
                        conn = sqlite3.connect('Databases/inventory_db.db')
                        cursor = conn.cursor()
                        pump_label = config[3]
                        #print(pump_label)
                        pump_id_row = cursor.execute("SELECT pump_id FROM pump WHERE pump_label = ?", (pump_label,)).fetchone()
                        pump_id = pump_id_row[0]
                        #print(pump_id)
                        shift_id_row = cursor.execute("Select shift_id FROM shift ORDER BY shift_id DESC LIMIT 1").fetchone()
                        shift_id = shift_id_row[0]
                        #print(shift_id)
                        cursor.execute('''
                                       INSERT INTO transactions(shift_id, pump_id, volume, price, Date)
                                       Values(?,?,?,?,?)
                                       ''',(shift_id, pump_id, volume_value, price_value, datenow))
                        conn.commit()
                        conn.close()
                except ValueError: 
                    #print(f"Invalid input in {config[3]}. Please enter numeric values.")
                    messagebox.showinfo("Input Error", f"Please enter the correct inputs in {config[3]}.")#type: ignore
            else:
                continue
                    
                # You can now use volume_value and price_value as needed
            self.clear()
    
    # Method to clear selected textbox
    def clearbox(self, textboxname: str, price: str):
        getattr(self, textboxname).config(state = "normal")
        getattr(self, textboxname).delete(0, tk.END)
        getattr(self, textboxname).insert(0, price)
        getattr(self, textboxname).config(state = "disabled")
    
    # Method to clear all textboxes
    def clear(self):
        for textbox in self.widget_configs: 
            getattr(self, textbox[5]).delete(0,tk.END)
            getattr(self, textbox[6]).config(state="normal")
            getattr(self, textbox[6]).delete(0,tk.END) 
            getattr(self, textbox[6]).config(state="disabled")                 
    
    #Method to handle button clicks TBR      
    def Onclick(self, button_number: int, entryname: str):
        self.clear()
        match button_number:
            case 1:
                #print("Diesel 1 clicked")
                self.activatetextbox(entryname)
                
            case 2:
                #print("Diesel 2 clicked")
                self.activatetextbox(entryname)

            case 3:
                #print("Premium 1 clicked")
                self.activatetextbox(entryname)

            case 4:
                #print("Premium 2 clicked")
                self.activatetextbox(entryname)

            case 5:
                #print("Premium 3 clicked")
                self.activatetextbox(entryname)

            case 6:
                #print("Unleaded clicked")  
                self.activatetextbox(entryname)
            case _: pass
     
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
    
    #Method to remove focus when a textbox is focused on
    def remove_focus(self, event: tk.Event):
        widget = event.widget
        if not isinstance(widget, ttk.Entry):
            try:
                if self.dummy_focus.winfo_exists():
                    self.dummy_focus.focus_set()
            except tk.TclError:
                pass  
    
    #Method to activate textbox
    def activatetextbox(self, textboxname: str):  
        getattr(self, textboxname).config(state = "normal")   
        getattr(self, textboxname).focus_set()
        for textbox in self.widget_configs:
            if textbox[5] != textboxname:
                getattr(self, textbox[5]).config(state = "disabled")            
            
class TransactionsPage(tk.Frame):
    def __init__(self, parent: tk.Frame):
        super().__init__(parent, bg='white')
        
        #Tree style
        style:ttk.Style = ttk.Style()
        style.theme_use('alt')
        style.configure("Custom.Treeview", #type: ignore
                        background="white",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="white") 
        
        #setting columns
        columns = ('Pump Label', 'Fuel_type', 'Volume(Liters)', 'Price(Pesos)', 'Date(YYYY/MM/DD)')
        
        #Make tree
        tree = ttk.Treeview(self, columns=columns, show='headings', style= "Custom.Treeview")
        for col in columns:
            tree.heading(col, text=col, anchor='w')
            tree.column(col, anchor='w', width=100)
        tree.pack(side='left', fill='both', expand=True)

        #Vertical scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=tree.yview) #type: ignore
        tree.configure(yscroll=scrollbar.set) # type: ignore
        scrollbar.pack(side='right', fill='y')

        # Event binding to remove focus
        def on_tree_click(event: tk.Event):
            region = tree.identify("region", event.x, event.y)#type: ignore
            if region != "cell":
                tree.selection_remove(tree.selection())

        tree.bind("<Button-1>", on_tree_click)

        connect = sqlite3.connect('Databases/inventory_db.db')
        cursor = connect.cursor()
        cursor.execute('''SELECT 
                       pump.pump_label AS "Pump_label", 
                       fuel_type.fuel_name AS "Fuel_type",
                       transactions.Volume, 
                       transactions.Price, 
                       transactions.Date 
                       FROM transactions
                       JOIN pump ON transactions.pump_id = pump.pump_id
                       JOIN fuel_type ON pump.fuel_type_id = fuel_type.fuel_type_id
                       ORDER BY transactions.transaction_id DESC''')
        rows = cursor.fetchall()
        connect.close()
        for i, values in enumerate(rows):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert('', 'end', values=values, tags=(tag,))
        tree.tag_configure('evenrow', background="#c6ccc6")
        tree.tag_configure('oddrow', background="#949994")
        style.map('Custom.Treeview', background=[('selected', "#627595")])#type: ignore
        
class PricePage(tk.Frame):
    def __init__(self, parent: tk.Frame):
        super().__init__(parent, bg='#91C4EE', bd=2, relief='solid')
        
        # Main container for centering content
        self.container = tk.Frame(self, bg='#91C4EE')
        self.container.pack(fill='both', expand=True)
        
        # Left frame (west)
        self.Current_Liter_Price = tk.Frame(self.container, bg="#ffffff", width=300, height=600,bd=2, relief='solid')
        self.Current_Liter_Price.pack(side='left', fill='y', padx=(50, 50), pady=30)
        
        self.tree_frame = tk.Frame(self.Current_Liter_Price, bg="#c1c9cb")
        self.tree_frame.pack(fill='both', expand=True)
    
        self.style:ttk.Style = ttk.Style()
        self.style.theme_use('alt')
        self.style.configure("Custom.Treeview", #type: ignore
                        background="white",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="white") 

        #setup columns
        self.columns = ('Fuel_type', 'Price', 'Effective_Date')
        
        # Create Treeview
        self.price_tree = ttk.Treeview(
            self.tree_frame,
            columns = self.columns,
            selectmode='browse',
            show='headings',
            height=15,
            style = "Custom.Treeview",
        )
        for col in self.columns:
            self.price_tree.heading(col, text=col, anchor='w')
            self.price_tree.column(col, anchor='w', width=100)
        self.price_tree.pack(side='left', fill='y', expand=True, padx =5, pady = 5)
        
        self.tree_scroll = ttk.Scrollbar(self.tree_frame, orient='vertical', command= self.price_tree.yview)# type: ignore
        self.price_tree.configure(yscroll= self.tree_scroll.set)# type: ignore
        self.tree_scroll.pack(side='left', fill='y')        
    
        self.style.map('Custom.Treeview', background=[('selected', "#627595")])#type: ignore
        
        self.refresh()
        
        self.price_tree.tag_configure('Diesel', background="#c6ccc6")
        self.price_tree.tag_configure('Premium', background="#949994")
        self.price_tree.tag_configure('Unleaded', background="#797D79")

        #============================================================================================================
        # Center frame
        self.EditPriceFrame = tk.Frame(
            self.container, 
            bg="#3498db", 
            width=650, 
            height=600,
            bd=0,
            relief='flat',
            highlightthickness=1,
            highlightbackground="#D1E0FF",
            highlightcolor="#D1E0FF",
            padx=15,
            pady=15
            )
        self.EditPriceFrame.pack(side='left', fill='both', expand=True, padx=(0, 20), pady=30)
        
        self.widgets = [("Diesel_Norm_Row","dieselnorm_button", "dieselnormentry", 1, "Diesel Change Price"), 
                   ("Premium_Norm_Row","premiumnorm_button", "premiumnormentry", 2, "Premium Change Price"), 
                   ("Unleaded_Norm_Row","unleadednorm_button", "unleadednormentry", 3, "Unleaded Change Price"),
                   ("Diesel100_Row","diesel100button", "diesel100entry", 4, "Diesel 100L Change Price"),
                   ("Premium100_Row","premium100button", "premium100entry", 5, "Premium 100L Change Price"), 
                   ("Unleaded100_Row","unleaded100button", "unleaded100entry", 6, "Unleaded 100L Change Price")]
        self.dummy_focus = tk.Frame(self)
        self.dummy_focus.place(x=0, y=0, width=1, height=1)
        
    
        # Configure grid layout with better spacing
        for r in range(6):
            self.EditPriceFrame.grid_rowconfigure(r, weight=1)
            self.EditPriceFrame.grid_columnconfigure(0, weight=1)
            # Modern card-like row design
            row = tk.Frame(
                self.EditPriceFrame, 
                bg="#ecf0f1", 
                bd=0,
                highlightthickness=1,
                highlightbackground="#F0F5FF",
                highlightcolor="#F0F5FF",
                padx=10,
                pady=5
            )
            row.grid(row=r, column=0, sticky="nsew", padx=5, pady=8)
            row.grid_propagate(False)
            row_name = self.widgets[r][0]
            setattr(self, row_name, row)
    
        # Styled button and entry widgets
        for row_name, buttonname, entryname, button_number, text in self.widgets:
            # Modern button design
            button = tk.Button(
            getattr(self, row_name),
            text=text,
            bg="#4A7EFF", 
            fg='white',
            font=("Segoe UI", 11, "bold"),
            bd=0,
            command=lambda n=button_number: self.Onclick(n, self.widgets[n-1][2]),
            padx=15,
            pady=8,
            relief='flat',
            cursor="hand2",
            activebackground="#3460CC",
            activeforeground="white",
            height=1,
            width=20
        )
            button.pack(side='left', fill='y', padx=(10, 5), pady=10)
            setattr(self, buttonname, button)
        
            # Modern entry design
            entry = ttk.Entry(
                getattr(self, row_name),
                width=15,
                font=("Segoe UI", 14),
                state='disabled',
                justify='center'
            )
            # Style configuration for entry
            style = ttk.Style()
            style.configure("Modern.TEntry", #type: ignore
                        fieldbackground="#F8FAFF", 
                        foreground="#333333",
                        bordercolor="#D1E0FF",
                        lightcolor="#D1E0FF",
                        darkcolor="#D1E0FF",
                        padding=(10, 8, 10, 8))
            style.map("Modern.TEntry", #type: ignore
                 fieldbackground=[("disabled", "#F8FAFF")],
                 foreground=[("disabled", "#4A4A4A")])
        
            entry.configure(style="Modern.TEntry")
            entry.pack(side='right', fill='both', expand=True, padx=(5, 15), pady=10)
            setattr(self, entryname, entry)

        # Right frame (east)
        self.Current_100L_Price = tk.Frame(
            self.container, 
            bg="#ffffff", 
            width=300, 
            height=600,
            bd=2, 
            relief='solid'
        )
        self.Current_100L_Price.pack(side='left', fill='y', padx=(50, 50), pady=30)
        
        self.tree100_frame = tk.Frame(self.Current_100L_Price, bg="#c1c9cb")
        self.tree100_frame.pack(fill='both', expand=True)
        
        self.columns100 = ('Fuel_type', 'Price', 'Effective_Date')
        # Create Treeview
        self.price100_tree = ttk.Treeview(
            self.tree100_frame,
            columns = self.columns,
            selectmode='browse',
            show='headings',
            height=15,
            style = "Custom.Treeview",
        )
        for col in self.columns100:
            self.price100_tree.heading(col, text=col, anchor='w')
            self.price100_tree.column(col, anchor='w', width=100)
        self.price100_tree.pack(side='left', fill='y', expand=True, padx =5, pady = 5)
        
        self.tree100_scroll = ttk.Scrollbar(self.tree100_frame, orient='vertical', command= self.price100_tree.yview)# type: ignore
        self.price100_tree.configure(yscroll= self.tree100_scroll.set)# type: ignore
        self.tree100_scroll.pack(side='left', fill='y')        
    
        self.style.map('Custom.Treeview', background=[('selected', "#627595")])#type: ignore
        
        self.refresh100()
        
        self.price100_tree.tag_configure('Diesel100', background="#c6ccc6")
        self.price100_tree.tag_configure('Premium100', background="#949994")
        self.price100_tree.tag_configure('Unleaded100', background="#797D79")
        
        self.bind_all("<Button-1>", self.remove_focus)
        self.selected = 0
        self.selected100 = 0
    
    #Method on the right side scrollbar
    def refresh100(self):
        for item in self.price100_tree.get_children():
            self.price100_tree.delete(item)
            
        connect = sqlite3.connect('Databases/inventory_db.db')
        cursor = connect.cursor()
        cursor.execute('''SELECT 
                       Name,
                       price,
                       effective_date
                       FROM price
                       WHERE Name IN ('Diesel100', 'Premium100', 'Unleaded100')
                       ORDER by Name ASC, price_id DESC
                       ''')
        rows = cursor.fetchall()
        for i, values in enumerate(rows):
            if rows[i][0] == "Diesel100":
                tag = 'Diesel100'
            elif rows[i][0] == "Premium100":
                tag = 'Premium100'
            elif rows[i][0] == "Unleaded100":
                tag = 'Unleaded100'
            else:
                tag = "Lol"
            self.price100_tree.insert('', 'end', values=values, tags=(tag,))  
        connect.close()
    
    #Method on the left side scrollbar
    def refresh(self):
        for item in self.price_tree.get_children():
            self.price_tree.delete(item)
            
        connect = sqlite3.connect('Databases/inventory_db.db')
        cursor = connect.cursor()
        cursor.execute('''SELECT 
                       Name,
                       price,
                       effective_date
                       FROM price
                       WHERE Name IN ('Diesel', 'Premium', 'Unleaded')
                       ORDER by Name ASC, price_id DESC
                       ''')
        rows = cursor.fetchall()
        for i, values in enumerate(rows):
            if rows[i][0] == "Diesel":
                tag = 'Diesel'
            elif rows[i][0] == "Premium":
                tag = 'Premium'
            elif rows[i][0] == "Unleaded":
                tag = 'Unleaded'
            else:
                tag = "Lol"
            self.price_tree.insert('', 'end', values=values, tags=(tag,))  
        connect.close()
    
    # Functionality when buttons are clicked    
    def Onclick(self, button_number: int, entryname: str):
        getattr(self, entryname).config(state ='normal')
        getattr(self, entryname).focus_set()
        match button_number:
            case 1:
                #print(f"Clicked {button_number}", entryname)
                self.clear(entryname)
                self.disable(entryname)
                value = getattr(self, entryname).get()
                self.getvalue(value, 1)
            case 2:
                #print(f"Clicked {button_number}", entryname)
                self.clear(entryname)
                self.disable(entryname)
                value = getattr(self, entryname).get()
                self.getvalue(value, 2)
            case 3:
                #print(f"Clicked {button_number}", entryname)
                self.clear(entryname)
                self.disable(entryname)
                value = getattr(self, entryname).get()
                self.getvalue(value, 3)
            case 4:
                #print(f"Clicked {button_number}", entryname)
                self.clear(entryname)
                self.disable(entryname)
                value = getattr(self, entryname).get()
                self.getvalue(value, 4)
            case 5:
                #print(f"Clicked {button_number}", entryname)
                self.clear(entryname)
                self.disable(entryname)
                value = getattr(self, entryname).get()
                self.getvalue(value, 5)
            case 6:   
                #print(f"Clicked {button_number}", entryname)
                self.clear(entryname)
                self.disable(entryname)
                value = getattr(self, entryname).get()
                self.getvalue(value, 6)
            case _: pass
               
    #function to get values
    def getvalue(self, value: str, number: int):
        #this is the number assigned to fuel types and its volume
        '''
        1 - Diesel
        2 - Premium
        3 - Unleaded
        4 - Diesel100
        5 - Premium100
        6 - Unleaded100
        '''
        
        number_id: int = number
        
        #try except to add values if they are appropriate and reject if not
        try:
            volumechange = float(value)
            print(f"value of {volumechange} is added")
            print(type(volumechange))
            self.clear(None)
            try:
                if self.dummy_focus.winfo_exists():
                    self.dummy_focus.focus_set()
            except tk.TclError:
                pass      
            self.addvalue(volumechange, number_id)
        except ValueError as e:
            print(f"{e}")
    
    #clear each textbox
    def clear(self, widget: str | None):
        for textbox in self.widgets: 
            if textbox[2] != widget:
                getattr(self, textbox[2]).delete(0,tk.END)  
     
    #disable each textbox              
    def disable(self, widget: str):
        for textbox in self.widgets: 
            if textbox[2] != widget:
                getattr(self, textbox[2]).config(state = 'disabled')  
    
    #add value to database            
    def addvalue(self, value: float, number_id: int):
        #passing values from other function
        fuel_type_id: int | None = 0
        Name: str | None = ""
        price: float | None = value
        datenow = datetime.datetime.now().strftime("%m-%d-%Y")
        
        #establishing connection
        conn = sqlite3.connect('Databases/inventory_db.db')
        cursor = conn.cursor()
        
        match number_id:
            case 1:
                fuel_type_id = 1
                Name = "Diesel"
            case 2:
                fuel_type_id = 2
                Name = "Premium"
            case 3:
                fuel_type_id = 3
                Name = "Unleaded"
            case 4:
                fuel_type_id = 1
                Name = "Diesel100"
            case 5:
                fuel_type_id = 2
                Name = "Premium100"
            case 6:
                fuel_type_id = 3
                Name = "Unleaded100"
            case _: pass  
        cursor.execute('''
                       INSERT INTO price(fuel_type_id, Name, price,effective_date)
                       Values(?,?,?,?)
                       ''', (fuel_type_id, Name, price,datenow))
        conn.commit()
        conn.close()
        self.refresh()
        self.refresh100()
    
    #remove focus    
    def remove_focus(self, event: tk.Event):
        widget = event.widget
        if not isinstance(widget, ttk.Entry):
            try:
                if self.selected: 
                    self.refresh()
                    self.selected = 0
                if self.selected100:
                    self.refresh100()
                    self.selected100 = 0
                if self.dummy_focus.winfo_exists():
                    self.dummy_focus.focus_set()
                    self.selected = self.price_tree.focus()
                    self.selected100 = self.price100_tree.focus()
            except tk.TclError:
                pass               
                
class DeliveryPage(tk.Frame):
    def __init__(self, parent:tk.Frame):
        super().__init__(parent, bg='white')
        tk.Label(self, text="Delivery Content").pack()

class InventoryPage(tk.Frame):
    def __init__(self, parent:tk.Frame):
        super().__init__(parent, bg='#91C4EE')
        
        # Frames for each fuel type (unchanged)
        self.left_frame = tk.Frame(self, bg = '#ffffff', width = 500, height = 600, bd = 2, relief = 'solid')
        self.left_frame.pack(side = 'left', fill = 'y', padx = 10, pady = 10)
        self.center_frame = tk.Frame(self, bg = '#ffffff', width = 500, height = 600, bd = 2, relief = 'solid')
        self.center_frame.pack(side = 'left', fill = 'y', padx = 10, pady = 10)
        self.right_frame = tk.Frame(self, bg = '#ffffff', width = 500, height = 600, bd = 2, relief = 'solid')
        self.right_frame.pack(side = 'left', fill = 'y', padx = 10, pady = 10)
        
        # Top and Bottom Frames for each fuel type
        self.upper_frame_left = tk.Frame(self.left_frame, bg = "#2c3e50", width = 500, height = 100, bd = 0, relief = 'flat')
        self.upper_frame_left.pack(side = 'top', fill = 'x')
        
        self.upper_frame_center = tk.Frame(self.center_frame, bg = "#2c3e50", width = 500, height = 100, bd = 0, relief = 'flat')
        self.upper_frame_center.pack(side = 'top', fill = 'x')
        
        self.upper_frame_right = tk.Frame(self.right_frame, bg = "#2c3e50", width = 500, height = 100, bd = 0, relief = 'flat')
        self.upper_frame_right.pack(side = 'top', fill = 'x')
        
        # Stylish Diesel label with decorative elements
        # Diesel
        diesel_container = tk.Frame(self.upper_frame_left, bg="#3498db", bd=0, highlightthickness=0,height=80)
        diesel_container.pack(side='top', fill='x', padx=10, pady=10, expand=True)
        tk.Frame(diesel_container, bg="#56e73c", width=100, height=80).pack(side='left', fill='y')
        tk.Label(diesel_container, text="DIESEL", bg="#3498db",  fg="white", font=('Segoe UI', 28, 'bold'), padx=20).pack(side='left', fill='both', expand=True)
        left_accent_frame = tk.Frame(diesel_container, bg="#3498db", width=50)
        left_accent_frame.pack(side='right', fill='y')
        tk.Label(left_accent_frame, text="⛽", bg="#3498db",fg="white",font=('Segoe UI', 28)).pack()
        
        # Premium
        premium_container = tk.Frame(self.upper_frame_center, bg="#3498db", bd=0, highlightthickness=0,height=80)
        premium_container.pack(side='top', fill='x', padx=10, pady=10, expand=True)
        tk.Frame(premium_container, bg="#56e73c", width=100, height=80).pack(side='left', fill='y')
        tk.Label(premium_container, text="PREMIUM", bg="#3498db",  fg="white", font=('Segoe UI', 28, 'bold'), padx=20).pack(side='left', fill='both', expand=True)
        center_accent_frame = tk.Frame(premium_container, bg="#3498db", width=50)
        center_accent_frame.pack(side='right', fill='y')
        tk.Label(center_accent_frame, text="⛽", bg="#3498db",fg="white",font=('Segoe UI', 28)).pack()
        
        # Unleaded
        unleaded_container = tk.Frame(self.upper_frame_right, bg="#3498db", bd=0, highlightthickness=0,height=80)
        unleaded_container.pack(side='top', fill='x', padx=10, pady=10, expand=True)
        tk.Frame(unleaded_container, bg="#56e73c", width=100, height=80).pack(side='left', fill='y')
        tk.Label(unleaded_container, text="UNLEADED", bg="#3498db",  fg="white", font=('Segoe UI', 28, 'bold'), padx=20).pack(side='left', fill='both', expand=True)
        right_accent_frame = tk.Frame(unleaded_container, bg="#3498db", width=50)
        right_accent_frame.pack(side='right', fill='y')
        tk.Label(right_accent_frame, text="⛽", bg="#3498db",fg="white",font=('Segoe UI', 28)).pack()
        
        #Lower Frames of each fuel type
        self.lower_frame_left = tk.Frame(self.left_frame, bg = "#e1e9ea", width = 500, height = 500)
        self.lower_frame_left.pack(side = 'top', fill = 'both', expand=True)
        
        self.lower_frame_center = tk.Frame(self.center_frame, bg = "#e1e9ea", width = 500, height = 500)
        self.lower_frame_center.pack(side = 'top', fill = 'both', expand=True)
        
        self.lower_frame_right = tk.Frame(self.right_frame, bg = "#e1e9ea", width = 500, height = 500)
        self.lower_frame_right.pack(side = 'top', fill = 'both', expand=True)
        
        conn = sqlite3.connect('Databases/inventory_db.db')
        cursor = conn.cursor()
        
        #halves of each lower frames
        
        #Left
        for frame in [self.lower_frame_left, self.lower_frame_center, self.lower_frame_right]:
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_columnconfigure(1, weight=1)
        
        self.left_income_frame = tk.Frame(self.lower_frame_left, bg = "#91C4EE", width = 250, height = 500, bd = 2, relief='solid')
        self.left_income_frame.grid(row = 0, column = 0, sticky='nsew')
        self.left_income_frame.columnconfigure(0, weight=1)
        self.left_income_frame.grid_propagate(False)
        
        self.left_volume_frame = tk.Frame(self.lower_frame_left, bg = "#91C4EE", width = 250, height = 500, bd = 2, relief='solid')
        self.left_volume_frame.grid(row = 0, column = 1, sticky='nsew')
        self.left_volume_frame.columnconfigure(0, weight=1)
        self.left_volume_frame.grid_propagate(False)
        
        #fetches income of diesel based on time
        cursor.execute("""
                       SELECT strftime('%Y-%d', Date) as Daily_Date,
                       SUM(CASE WHEN pump_id = 1 or pump_id = 2 THEN price ELSE 0 END) as Daily_Total_income
                       FROM transactions
                       GROUP BY Daily_Date
                       ORDER BY Daily_Date DESC
                       LIMIT 1
                       """)
        daily_diesel_row = cursor.fetchone()
        cursor.execute("""
                       SELECT strftime('%Y-%W', Date) as Weekly_Date,
                       SUM(CASE WHEN pump_id =  1 or pump_id = 2 THEN price ELSE 0 END) AS total_price_pump
                       FROM transactions
                       GROUP BY Weekly_Date
                       ORDER BY Weekly_Date DESC
                       LIMIT 1
                       """)
        weekly_diesel_row = cursor.fetchone()
        cursor.execute("""
                       SELECT strftime('%Y-%m', Date) as Monthly_Date,
                       SUM(CASE WHEN pump_id =  1 or pump_id = 2 THEN price ELSE 0 END) AS total_price_pump
                       FROM transactions
                       GROUP BY Monthly_Date
                       ORDER BY Monthly_Date DESC
                       LIMIT 1
                       """)
        monthly_diesel_row = cursor.fetchone()
        cursor.execute("""
                       SELECT strftime('%Y', Date) as Yearly_Date,
                       SUM(CASE WHEN pump_id =  1 or pump_id = 2 THEN price ELSE 0 END) AS total_price_pump
                       FROM transactions
                       GROUP BY Yearly_Date
                       ORDER BY Yearly_Date DESC
                       LIMIT 1
                       """)
        yearly_diesel_row = cursor.fetchone()
        cursor.execute("""
                       SELECT
                       SUM(CASE WHEN pump_id =  1 or pump_id = 2 THEN price ELSE 0 END) AS total_price_pump
                       FROM transactions
                       """)
        lifetime_diesel_row = cursor.fetchone()
        
        #creates and puts the income information into the labels
        daily_income_diesel_label = tk.Label(self.left_income_frame,
                                             text = f"Daily Income \n-------------------------------\n₱{daily_diesel_row[1]}",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        daily_income_diesel_label.grid(row=0, column=0, sticky="nsew", pady=30)
        
        weekly_income_diesel_label = tk.Label(self.left_income_frame,
                                             text = f"Weekly Income \n-------------------------------\n₱{weekly_diesel_row[1]}",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        weekly_income_diesel_label.grid(row=1, column=0, sticky="nsew", pady=30)
        
        monthly_income_diesel_label = tk.Label(self.left_income_frame,
                                             text = f"Monthly Income \n-------------------------------\n₱{monthly_diesel_row[1]}",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        monthly_income_diesel_label.grid(row=2, column=0, sticky="nwsew", pady=30)
        
        yearly_income_diesel_label = tk.Label(self.left_income_frame,
                                             text = f"Yearly Income \n-------------------------------\n₱{yearly_diesel_row[1]}",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        yearly_income_diesel_label.grid(row=3, column=0, sticky="nsew", pady=30)
        
        lifetime_income_diesel_label = tk.Label(self.left_income_frame,
                                             text = f"Lifetime Income \n-------------------------------\n₱{lifetime_diesel_row[0]}",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        lifetime_income_diesel_label.grid(row=3, column=0, sticky="nsew", pady=30)
        
        #fetches both lifetime and daily volume
        cursor.execute("""
                       SELECT
                       SUM(CASE WHEN pump_id = 1 THEN volume ELSE 0 END),
                       SUM(CASE WHEN pump_id = 2 THEN volume ELSE 0 END)
                       FROM transactions
                       """)
        diesel_volumes_lifetime = cursor.fetchone()
        cursor.execute("""
                       SELECT
                       strftime('%Y-%m-%d', Date) AS daily_date,
                       SUM(CASE WHEN pump_id = 1 THEN volume ELSE 0 END) AS daily_volume_pump_1,
                       SUM(CASE WHEN pump_id = 2 THEN volume ELSE 0 END) AS daily_volume_pump_2
                       FROM transactions
                       GROUP BY daily_date  
                       ORDER BY daily_date DESC
                       LIMIT 1;
                       """)
        diesel_volumes_daily = cursor.fetchone()
        
        #creates and puts volume 
        lifetime_volume_diesel1_label = tk.Label(self.left_volume_frame,
                                             text = f"Lifetime Volume Pump 1\n------------------------------\n{diesel_volumes_lifetime[0]} Liters",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        lifetime_volume_diesel1_label.grid(row=0, column=0, sticky="nsew", pady=30)
        
        lifetime_volume_diesel2_label = tk.Label(self.left_volume_frame,
                                             text = f"Lifetime Volume Pump 2\n------------------------------\n{diesel_volumes_lifetime[1]} Liters",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        lifetime_volume_diesel2_label.grid(row=1, column=0, sticky="nsew", pady=30)
        
        daily_volume_diesel1_label = tk.Label(self.left_volume_frame,
                                             text = f"Daily Volume Pump 1\n------------------------------\n{diesel_volumes_daily[1]} Liters",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        daily_volume_diesel1_label.grid(row=2, column=0, sticky="nsew", pady=30)
        
        daily_volume_diesel2_label = tk.Label(self.left_volume_frame,
                                             text = f"Daily Volume Pump 2\n------------------------------\n{diesel_volumes_daily[2]} Liters",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        daily_volume_diesel2_label.grid(row=3, column=0, sticky="nsew", pady=30)
        
        #Center
        self.center_income_frame = tk.Frame(self.lower_frame_center, bg = "#91C4EE", width = 250, height = 500, bd = 2, relief='solid')
        self.center_income_frame.grid(row = 0, column = 0, sticky='nsew')
        self.center_income_frame.grid_propagate(False)
        self.center_income_frame.columnconfigure(0, weight= 1)
        
        self.center_volume_frame = tk.Frame(self.lower_frame_center, bg = "#91C4EE", width = 250, height = 500, bd = 2, relief='solid')
        self.center_volume_frame.grid(row = 0, column = 1, sticky='nsew')
        self.center_volume_frame.grid_propagate(False)
        self.center_volume_frame.columnconfigure(0, weight= 1)
        
        #fetches income of premium based on time
        cursor.execute("""
                       SELECT strftime('%Y-%d', Date) as Daily_Date,
                       SUM(CASE WHEN pump_id = 3 or pump_id = 4 or pump_id = 5 THEN price ELSE 0 END)
                       FROM transactions
                       GROUP BY Daily_Date
                       ORDER BY Daily_Date DESC
                       LIMIT 1
                       """)
        daily_premium_row = cursor.fetchone()
        cursor.execute("""
                       SELECT strftime('%Y-%W', Date) as Weekly_Date,
                       SUM(CASE WHEN pump_id = 3 or pump_id = 4 or pump_id = 5 THEN price ELSE 0 END)
                       FROM transactions
                       GROUP BY Weekly_Date
                       ORDER BY Weekly_Date DESC
                       LIMIT 1
                       """)
        weekly_premium_row = cursor.fetchone()
        cursor.execute("""
                       SELECT strftime('%Y-%m', Date) as Monthly_Date,
                       SUM(CASE WHEN pump_id = 3 or pump_id = 4 or pump_id = 5 THEN price ELSE 0 END)
                       FROM transactions
                       GROUP BY Monthly_Date
                       ORDER BY Monthly_Date DESC
                       LIMIT 1
                       """)
        monthly_premium_row = cursor.fetchone()
        cursor.execute("""
                       SELECT strftime('%Y', Date) as Yearly_Date,
                       SUM(CASE WHEN pump_id = 3 or pump_id = 4 or pump_id = 5 THEN price ELSE 0 END)
                       FROM transactions
                       GROUP BY Yearly_Date
                       ORDER BY Yearly_Date DESC
                       LIMIT 1
                       """)
        yearly_premium_row = cursor.fetchone()
        cursor.execute("""
                       SELECT
                       SUM(CASE WHEN pump_id = 3 or pump_id = 4 or pump_id = 5 THEN price ELSE 0 END)
                       FROM transactions
                       """)
        lifetime_premium_row = cursor.fetchone()
        
        #creates and puts the income information into the labels
        daily_income_premium_label = tk.Label(self.center_income_frame,
                                             text = f"Daily Income \n-------------------------------\n₱{daily_premium_row[1]}",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        daily_income_premium_label.grid(row=0, column=0, sticky="nsew", pady=7)
        
        weekly_income_premium_label = tk.Label(self.center_income_frame,
                                             text = f"Weekly Income \n-------------------------------\n₱{weekly_premium_row[1]}",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        weekly_income_premium_label.grid(row=1, column=0, sticky="nsew", pady=7)
        
        monthly_income_premium_label = tk.Label(self.center_income_frame,
                                             text = f"Monthly Income \n-------------------------------\n₱{monthly_premium_row[1]}",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        monthly_income_premium_label.grid(row=2, column=0, sticky="nwsew", pady=7)
        
        yearly_income_premium_label = tk.Label(self.center_income_frame,
                                             text = f"Yearly Income \n-------------------------------\n₱{yearly_premium_row[1]}",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        yearly_income_premium_label.grid(row=3, column=0, sticky="nsew", pady=7)
        
        lifetime_income_premium_label = tk.Label(self.center_income_frame,
                                             text = f"Lifetime Income \n-------------------------------\n₱{lifetime_premium_row[0]}",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        lifetime_income_premium_label.grid(row=3, column=0, sticky="nsew", pady=7)
        
        #fetches both lifetime and daily volume
        cursor.execute("""
                       SELECT
                       SUM(CASE WHEN pump_id = 3 THEN volume ELSE 0 END),
                       SUM(CASE WHEN pump_id = 4 THEN volume ELSE 0 END),
                       SUM(CASE WHEN pump_id = 5 THEN volume ELSE 0 END)
                       FROM transactions
                       """)
        premium_volumes_lifetime = cursor.fetchone()
        cursor.execute("""
                       SELECT
                       strftime('%Y-%m-%d', Date) as Daily_Date,
                       SUM(CASE WHEN pump_id = 3 THEN volume ELSE 0 END),
                       SUM(CASE WHEN pump_id = 4 THEN volume ELSE 0 END),
                       SUM(CASE WHEN pump_id = 5 THEN volume ELSE 0 END)
                       FROM transactions
                       GROUP BY Daily_Date
                       ORDER BY Daily_Date DESC
                       LIMIT 1
                       """)
        premium_volumes_daily = cursor.fetchone()
        
        #creates and puts volume 
        lifetime_volume_premium1_label = tk.Label(self.center_volume_frame,
                                             text = f"Lifetime Volume Pump 1\n------------------------------\n{premium_volumes_lifetime[0]} Liters",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        lifetime_volume_premium1_label.grid(row=0, column=0, sticky="nsew", pady=7)
        
        lifetime_volume_premium2_label = tk.Label(self.center_volume_frame,
                                             text = f"Lifetime Volume Pump 2\n------------------------------\n{premium_volumes_lifetime[1]} Liters",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        lifetime_volume_premium2_label.grid(row=1, column=0, sticky="nsew", pady=7)
        
        lifetime_volume_premium3_label = tk.Label(self.center_volume_frame,
                                             text = f"Lifetime Volume Pump 3\n------------------------------\n{premium_volumes_lifetime[2]} Liters",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        lifetime_volume_premium3_label.grid(row=2, column=0, sticky="nsew", pady=7)
        
        daily_volume_premium1_label = tk.Label(self.center_volume_frame,
                                             text = f"Daily Volume Pump 1\n------------------------------\n{premium_volumes_daily[1]} Liters",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        daily_volume_premium1_label.grid(row=3, column=0, sticky="nsew", pady=7)
        
        daily_volume_premium2_label = tk.Label(self.center_volume_frame,
                                             text = f"Daily Volume Pump 2\n------------------------------\n{premium_volumes_daily[2]} Liters",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        daily_volume_premium2_label.grid(row=4, column=0, sticky="nsew", pady=7)
        
        daily_volume_premium3_label = tk.Label(self.center_volume_frame,
                                             text = f"Daily Volume Pump 3\n------------------------------\n{premium_volumes_daily[3]} Liters",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        daily_volume_premium3_label.grid(row=5, column=0, sticky="nsew", pady=7)
        
        #Right
        
        self.right_income_frame = tk.Frame(self.lower_frame_right, bg = "#91C4EE", width = 250, height = 500, bd = 2, relief='solid')
        self.right_income_frame.grid(row = 0, column = 0, sticky='nsew')
        self.right_income_frame.grid_propagate(False)
        self.right_income_frame.columnconfigure(0, weight= 1)
        
        self.right_volume_frame = tk.Frame(self.lower_frame_right, bg = "#91C4EE", width = 250, height = 500, bd = 2, relief='solid')
        self.right_volume_frame.grid(row = 0, column = 1, sticky='nsew')
        self.right_volume_frame.grid_propagate(False)
        self.right_volume_frame.columnconfigure(0, weight= 1)
        
        #fetches income of unleaded based on time
        cursor.execute("""
                       SELECT strftime('%Y-%d', Date) as Daily_Date,
                       SUM(CASE WHEN pump_id = 6 THEN price ELSE 0 END)
                       FROM transactions
                       GROUP BY Daily_Date 
                       ORDER BY Daily_Date DESC
                       LIMIT 1
                       """)
        daily_unleaded_row = cursor.fetchone()
        cursor.execute("""
                       SELECT strftime('%Y-%W', Date) as Weekly_Date,
                       SUM(CASE WHEN pump_id = 6 THEN price ELSE 0 END)
                       FROM transactions
                       GROUP BY Weekly_Date
                       ORDER BY Weekly_Date DESC
                       LIMIT 1
                       """)
        weekly_unleaded_row = cursor.fetchone()
        cursor.execute("""
                       SELECT strftime('%Y-%m', Date) as Monthly_Date,
                       SUM(CASE WHEN pump_id = 6 THEN price ELSE 0 END)
                       FROM transactions
                       GROUP BY Monthly_Date
                       ORDER BY Monthly_Date DESC
                       LIMIT 1
                       """)
        monthly_unleaded_row = cursor.fetchone()
        cursor.execute("""
                       SELECT strftime('%Y', Date) as Yearly_Date,
                       SUM(CASE WHEN pump_id = 6 THEN price ELSE 0 END)
                       FROM transactions
                       GROUP BY Yearly_Date
                       ORDER BY Yearly_Date DESC
                       LIMIT 1
                       """)
        yearly_unleaded_row = cursor.fetchone()
        cursor.execute("""
                       SELECT
                       SUM(CASE WHEN pump_id = 6 THEN price ELSE 0 END)
                       FROM transactions
                       """)
        lifetime_premium_row = cursor.fetchone()
        
        #creates and puts the income information into the labels
        daily_income_unleaded_label = tk.Label(self.right_income_frame,
                                             text = f"Daily Income \n-------------------------------\n₱{daily_unleaded_row[1]}",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        daily_income_unleaded_label.grid(row=0, column=0, sticky="nsew", pady=20)
        
        weekly_income_unleaded_label = tk.Label(self.right_income_frame,
                                             text = f"Weekly Income \n-------------------------------\n₱{weekly_unleaded_row[1]}",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        weekly_income_unleaded_label.grid(row=1, column=0, sticky="nsew", pady=20)
        
        monthly_income_unleaded_label = tk.Label(self.right_income_frame,
                                             text = f"Monthly Income \n-------------------------------\n₱{monthly_unleaded_row[1]}",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        monthly_income_unleaded_label.grid(row=2, column=0, sticky="nwsew", pady=20)
        
        yearly_income_unleaded_label = tk.Label(self.right_income_frame,
                                             text = f"Yearly Income \n-------------------------------\n₱{yearly_unleaded_row[1]}",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        yearly_income_unleaded_label.grid(row=3, column=0, sticky="nsew", pady=20)
        
        lifetime_income_unleaded_label = tk.Label(self.right_income_frame,
                                             text = f"Lifetime Income \n-------------------------------\n₱{lifetime_premium_row[0]}",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        lifetime_income_unleaded_label.grid(row=3, column=0, sticky="nsew", pady=20)
        
        #fetches both lifetime and daily volume
        cursor.execute("""
                       SELECT
                       SUM(CASE WHEN pump_id = 6 THEN volume ELSE 0 END)
                       FROM transactions
                       """)
        unleaded_volumes_lifetime = cursor.fetchone()
        cursor.execute("""
                       SELECT
                       strftime('%Y-%m-%d', Date) as Daily_Date,
                       SUM(CASE WHEN pump_id = 6 THEN volume ELSE 0 END)
                       FROM transactions
                       GROUP BY Daily_Date
                       ORDER BY Daily_Date DESC
                       LIMIT 1
                       """)
        unleaded_volumes_daily = cursor.fetchone()
        
        #creates and puts volume 
        lifetime_volume_unleaded_label = tk.Label(self.right_volume_frame,
                                             text = f"Lifetime Volume Pump 1\n------------------------------\n{unleaded_volumes_lifetime[0]} Liters",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        lifetime_volume_unleaded_label.grid(row=0, column=0, sticky="nsew", pady=20)
        
        daily_volume_unleaded_label = tk.Label(self.right_volume_frame,
                                             text = f"Daily Volume Pump 1\n------------------------------\n{unleaded_volumes_daily[1]} Liters",
                                             fg = "#131414",
                                             bg = '#3498db',
                                             font=("Segoe UI", 14)
                                            )
        daily_volume_unleaded_label.grid(row=1, column=0, sticky="nsew", pady=20)
        
        
        conn.close()
        


# --- Run program ---
setup_database()
projectframe = ProjectFrame()
projectframe.mainloop()