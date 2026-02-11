import hashlib
import secrets


class PasswordHasher:
    """
    Handles password hashing, salting, and verification using SHA-256.
    """

    def __init__(self, rounds: int = 6):
        self.rounds = rounds

    def generate_salt(self) -> str:
        return secrets.token_hex(2)

    def sha256_hash(self, data: bytes) -> bytes:
        """
        Applies SHA-256 hashing to input bytes.
        """
        return hashlib.sha256(data).digest()

    def mix_state(self, state: int, value: int) -> int:
        """
        Performs bitwise mixing to enhance the avalanche effect.
        """
        # XOR manipulation
        state ^= value

        # Bit rotation (left rotate by 7 bits)
        state = ((state << 7) | (state >> (64 - 7))) & ((1 << 64) - 1)

        # Multiplication introduces diffusion
        state = (state * 0x9E3779B97F4A7C15) & ((1 << 64) - 1)

        return state

    def hash_password(self, password: str, salt: str) -> str:
        """
        Hashes a password using SHA-256 combined with salt and multiple rounds
        of bitwise manipulation.
        """
        combined = (password + salt).encode("utf-8")
        hash_bytes = self.sha256_hash(combined)

        # Convert first 8 bytes to 64-bit state
        state = int.from_bytes(hash_bytes[:8], byteorder="big")

        for _ in range(self.rounds):
            for byte in hash_bytes:
                state = self.mix_state(state, byte)

            hash_bytes = self.sha256_hash(state.to_bytes(8, byteorder="big"))

        return f"{state:016x}"

    def create_password_record(self, password: str) -> dict:
        """
        Creates a secure password record to be stored in the database.
        """
        salt = self.generate_salt()
        hashed_password = self.hash_password(password, salt)

        return {
            "salt": salt,
            "rounds": self.rounds,
            "hash": hashed_password
        }

    def verify_password(self, input_password: str, stored_salt: str, stored_hash: str) -> bool:
        """
        Verifies an entered password against the stored hash.
        """
        return self.hash_password(input_password, stored_salt) == stored_hash
    
import hashlib
import secrets
import sqlite3
import re


DB_PATH = "marketanalysis_2.db"


class PasswordHasher:
    """
    Handles password hashing, salting, and verification using SHA-256.
    """

    def __init__(self, rounds: int = 6):
        self.rounds = rounds

    def generate_salt(self) -> str:
        return secrets.token_hex(2)  # 16-bit salt

    def sha256_hash(self, data: bytes) -> bytes:
        return hashlib.sha256(data).digest()

    def mix_state(self, state: int, value: int) -> int:
        state ^= value
        state = ((state << 7) | (state >> (64 - 7))) & ((1 << 64) - 1)
        state = (state * 0x9E3779B97F4A7C15) & ((1 << 64) - 1)
        return state

    def hash_password(self, password: str, salt: str) -> str:
        combined = (password + salt).encode("utf-8")
        hash_bytes = self.sha256_hash(combined)
        state = int.from_bytes(hash_bytes[:8], "big")

        for _ in range(self.rounds):
            for byte in hash_bytes:
                state = self.mix_state(state, byte)
            hash_bytes = self.sha256_hash(state.to_bytes(8, "big"))

        return f"{state:016x}"

    def create_password_record(self, password: str) -> dict:
        salt = self.generate_salt()
        return {
            "salt": salt,
            "hash": self.hash_password(password, salt)
        }

    def verify_password(self, password: str, salt: str, stored_hash: str) -> bool:
        return self.hash_password(password, salt) == stored_hash


class AuthTester:
    """
    Text-based authentication tester with clear user feedback.
    """

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.hasher = PasswordHasher()

    # ---------- SIGN UP ----------
    def signup(self):
        print("\n=== SIGN UP ===")
        username = input("Username: ")
        password = input("Password: ")
        confirm = input("Confirm Password: ")

        if not username or not password or not confirm:
            print("ERROR: Please fill in all fields.")
            return

        if not re.match(r"^\w+$", username):
            print("ERROR: Username can only contain letters, numbers, and underscores.")
            return

        if len(password) < 8:
            print("ERROR: Password must be at least 8 characters long.")
            return

        if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
            print("ERROR: Password must include letters and numbers.")
            return

        if password != confirm:
            print("ERROR: Passwords do not match.")
            return

        self.cursor.execute("SELECT 1 FROM USER WHERE username = ?", (username,))
        if self.cursor.fetchone():
            print("ERROR: This username is already taken.")
            return

        record = self.hasher.create_password_record(password)

        self.cursor.execute(
            "INSERT INTO USER (username, salt, hashedPassword) VALUES (?, ?, ?)",
            (username, record["salt"], record["hash"])
        )
        self.conn.commit()

        print("SUCCESS: Account created.")

    # ---------- LOGIN ----------
    def login(self):
        print("\n=== LOGIN ===")
        username = input("Username: ")
        password = input("Password: ")

        if not username or not password:
            print("ERROR: Please fill in all fields.")
            return

        self.cursor.execute(
            "SELECT salt, hashedPassword FROM USER WHERE username = ?",
            (username,)
        )
        result = self.cursor.fetchone()

        if not result:
            print("ERROR: This user does not exist. Please sign up first.")
            return

        salt, stored_hash = result

        if self.hasher.verify_password(password, salt, stored_hash):
            print("SUCCESS: Login successful.")
            print("Session token:", secrets.token_hex(16))
        else:
            print("ERROR: Incorrect password for this user.")

    def close(self):
        self.conn.close()


# ---------- MAIN ----------
if __name__ == "__main__":
    tester = AuthTester()

    while True:
        print("\n1. Sign Up")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose option: ")

        if choice == "1":
            tester.signup()
        elif choice == "2":
            tester.login()
        elif choice == "3":
            tester.close()
            print("Program closed.")
            break
        else:
            print("Invalid option.")