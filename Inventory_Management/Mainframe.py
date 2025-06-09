import tkinter as tk
from PIL import Image, ImageTk 
from tkinter import messagebox
from tkinter import simpledialog
import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def setup_usersdatabase():
    conn = sqlite3.connect('Databases/users.db')
    cursor = conn.cursor()
    # Create the users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    # Check if the table is empty
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        # Ask for a new admin password using a popup
        root = tk.Tk()
        root.withdraw()  # Hide the root window
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
    conn = sqlite3.connect('Databases/users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM users WHERE username=?', (username,))
    dbpass = cursor.fetchone()
    conn.close()
    if dbpass and hash_password(password) == dbpass[0]:
        return True
    return False

#setup the login page
def loginpagesetup(): 
    #loginpage
    loginpage = tk.Tk()
    loginpage.title("Inventory Management System")
    loginpage.configure(bg='lightblue')

    screen_width = loginpage.winfo_screenwidth()
    screen_height = loginpage.winfo_screenheight()

    window_width = int(screen_width * 0.8)
    window_height = int(screen_height * 0.8)

    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    loginpage.geometry(f"{window_width}x{window_height}+{x}+{y}")
    loginpage.state('zoomed')
    
    #Title Label
    titlelabel = tk.Label(loginpage, text="(Gas station name) Inventory Management System", font=("Arial", 24), bg='blue')
    titlelabel.pack(pady=20)
    
    # Picture logo
    # Debug path if error occurs
    img = Image.open(r"images\loginpicture.png")
    img = img.resize((200, 200)) 
    logo = ImageTk.PhotoImage(img)
    logolabel = tk.Label(loginpage, image=logo, bg='lightblue')
    logolabel.image = logo 
    logolabel.pack(pady=10)
    
    # Username 
    username_frame = tk.Frame(loginpage, bg='red')
    username_label = tk.Label(username_frame, text="Username:", font=("Arial", 14), bg='lightblue')
    username_label.pack(side="left", padx=(0, 10))
    usernametextbox = tk.Entry(username_frame, width=30, font=("Arial", 14), bg='white')
    usernametextbox.pack(side="left")
    usernametextbox.focus_set() 
    username_frame.pack(pady=10)

    # Password 
    password_frame = tk.Frame(loginpage, bg='red')
    password_label = tk.Label(password_frame, text="Password:", font=("Arial", 14), bg='lightblue')
    password_label.pack(side="left", padx=(0, 10))
    passwordtextbox = tk.Entry(password_frame, show='*', width=30, font=("Arial", 14), bg='white')
    passwordtextbox.pack(side="left")
    password_frame.pack(pady=10)

    # Login button
    def Onclick():
        username = usernametextbox.get()
        password = passwordtextbox.get()
        if check_login(username, password):
            messagebox.showinfo("Access granted!!", f"Welcome, {username}!")
        else:
            messagebox.showerror("Access denied", "Invalid username or password.")

    loginbutton = tk.Button(loginpage, text="Login", font=("Arial", 14), bg='green', fg='white', command=Onclick)
    loginbutton.pack(pady=10)
    loginbutton.bind("<Return>", lambda event: Onclick())
    
    #Event handlers for actions
    def focus_password(event):
        passwordtextbox.focus_set()
        return "break"

    def focus_username(event):
        usernametextbox.focus_set()
        return "break"
    
    def focus_login(event):
        loginbutton.focus_set()
        return "break"
    
    usernametextbox.bind("<Return>", focus_password)
    usernametextbox.bind("<Down>", focus_password)
    passwordtextbox.bind("<Up>", focus_username)
    passwordtextbox.bind("<Down>", focus_login)
    passwordtextbox.bind("<Return>", lambda event: Onclick())
    loginbutton.bind("<Up>", focus_password)
    
    
    return loginpage

setup_usersdatabase()

#main body of the program
loginpage = loginpagesetup()
loginpage.mainloop()