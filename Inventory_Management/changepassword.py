import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def change_password(username, new_password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    new_hash = hash_password(new_password)
    cursor.execute(
        'UPDATE users SET password_hash=? WHERE username=?',
        (new_hash, username)
    )
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    if updated:
        print(f"Password for '{username}' changed successfully!")
    else:
        print(f"User '{username}' not found.")

if __name__ == "__main__":
    user = input("Enter username: ")
    new_pass = input("Enter new password: ")
    change_password(user, new_pass)