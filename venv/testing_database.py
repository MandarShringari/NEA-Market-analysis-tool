import re
import secrets
import sqlite3

from hashingalgorithm import PasswordHasher


DB_PATH = "marketanalysis_2.db"


class AuthTester:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.hasher = PasswordHasher(rounds=6)
        self.session_token = None

    def validate_signup(self, username, password, confirm):
        if not username or not password or not confirm:
            return "Please fill in all fields."
        if not re.match(r"^\w+$", username):
            return "Username can only contain letters, numbers, and underscores."
        self.cursor.execute("SELECT 1 FROM USER WHERE username = ?;", (username,))
        if self.cursor.fetchone():
            return "This username is already taken."
        if len(password) < 8:
            return "Password must be at least 8 characters long."
        if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
            return "Password must include letters and numbers."
        if password != confirm:
            return "Passwords do not match."
        return None

    def signup(self):
        print("\n=== SIGN UP ===")
        username = input("Username: ")
        password = input("Password: ")
        confirm = input("Confirm Password: ")

        error = self.validate_signup(username, password, confirm)
        if error:
            print(error)
            return

        record = self.hasher.create_password_record(password)
        self.cursor.execute(
            """
            INSERT INTO USER (username, salt, hashedPassword)
            VALUES (?, ?, ?);
            """,
            (username, record["salt"], record["hash"]),
        )
        self.conn.commit()
        print("Account created successfully.")

    def login(self):
        print("\n=== LOGIN ===")
        username = input("Username: ")
        password = input("Password: ")

        if not username or not password:
            print("Please fill in all fields.")
            return

        self.cursor.execute(
            """
            SELECT salt, hashedPassword
            FROM USER
            WHERE username = ?;
            """,
            (username,),
        )
        result = self.cursor.fetchone()
        if not result:
            print("Invalid username or password.")
            return

        salt, stored_hash = result
        if self.hasher.verify_password(password, salt, stored_hash):
            self.session_token = secrets.token_hex(16)
            print("Login successful.")
            print(f"Session token created: {self.session_token}")
        else:
            print("Invalid username or password.")

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    auth = AuthTester()
    try:
        while True:
            print("\n1. Sign Up")
            print("2. Login")
            print("3. Exit")
            choice = input("Choose option: ").strip()

            if choice == "1":
                auth.signup()
            elif choice == "2":
                auth.login()
            elif choice == "3":
                print("Program closed.")
                break
            else:
                print("Invalid option.")
    finally:
        auth.close()
