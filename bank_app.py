import sqlite3
import hashlib
import random 
import time
from getpass import getpass

DB_NAME = "bank.db"

def start_up():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL CHECK(LENGTH(full_name) >= 4 AND LENGTH(full_name) <= 255),
                username TEXT NOT NULL UNIQUE CHECK(username <> ''),
                password TEXT NOT NULL CHECK(password <> ''),
                initial_balance INTEGER CHECK(initial_balance <> ''),
                account_number INTEGER CHECK(account_number <> '')
            );
                       
""")
        
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
           CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                transaction_type TEXT NOT NULL CHECK(transaction_type <> ''),
                amount INTEGER CHECK(amount > 0),
                transaction_date TEXT NOT NULL,
                recipient_acc TEXT,

                FOREIGN KEY (user_id) REFERENCES customers(id)
            );
""")
    
# ______________________________________________________Validation Section________________________________________

def collect_input_and_validate(field_name):
    while True:
        value = input(f"Enter your {field_name}: ").strip()

        if not value:
            print(f"{field_name} is required.")
            continue
        return value
    
# _____________________________________________________Account Opening Section_______________________________________________

def open_account():
    first_name = collect_input_and_validate("First name").strip()
    last_name = collect_input_and_validate("Last name")
    username = collect_input_and_validate("Username")

    while True:
        password = getpass("Enter your password: ").strip()
        if len(password) < 8 or len(password) > 30:
            print("The password most not be less than 8 and not greater than 30 ")
            continue

        if not password:
            print("Password is required.")
            continue

        confirm_password = getpass("Confirm your password: ").strip()
        if password != confirm_password:
            print("Passwords don't match.")
            continue
        break


    while True:
        try:
            initial_balance = int(input("Enter amount to open account: "))
        except ValueError:
            print("Amount most not be a non_numberic value")
            continue

        if initial_balance < 0:
            print("Amount most not be in negative value")
            continue
        elif initial_balance < 2000:
            print("Amount most be ₦2000 and above")
            continue
        elif initial_balance >= 2000:
            print("Opening balance Successfully deposited")
            break

    def gen_account_number():
        while True:
            account_number = str(random.randint(10000000, 99999999))  # 10-digit number
            
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM customers WHERE account_number = ?", (account_number,))
                exists = cursor.fetchone()

            if not exists:
                return account_number

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            cursor.execute("INSERT INTO customers (full_name, username, password, initial_balance, account_number) VALUES (?, ?, ?, ?, ?)", (first_name + " " + last_name, username, hashed_password, initial_balance, gen_account_number()))
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                print("Username is already taken")
            else:
                print("A user with those details already exists")
            return
        print("Verifying account...")
        time.sleep(5)
        print(f"account is open successfully!!! welcome to Firstbank {first_name} ")
    print("***************************************************")

# _________________________________________________________Login Section_________________________________________________


def login():
    username = collect_input_and_validate("Username")

    while True:
        password = getpass("Enter your password: ").strip()
        if not password:
            print("Password is required.")
            continue
        break

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        user = cursor.execute("SELECT id FROM customers WHERE username = ? AND password = ?", (username, hashed_password)).fetchone()

        if user is not None:
            user_id = user[0]
            print("Verifying account...")
            time.sleep(3)
            print("Connecting to bank server...")
            time.sleep(5)
            print("Login Successful")
            dashboard(user_id, username)
        else:
            print("Invalid credentials")
    print("***************************************************")

# _____________________________________________________________Dashboard Section_____________________________________

def dashboard(user_id, username):
    print(f"Welcome to your dashboard, {username} 👋")
    menu = """
1. withdraw
2. Deposit
3. Transaction history
4. Balance Enquiry
5. Transfer
6. Account Details
7. Quit
"""
    print(menu)

    while True:
        choice = input("Enter a trasaction to perform ")
        if choice == "1":
            withdraw(user_id, username)
        elif choice == "2":
            deposit(user_id, username)
        elif choice == "3":
            trans_history(user_id, username)
        elif choice == "4":
            balance_enquiry(user_id, username)
        elif choice == "5":
            transfer(user_id, username)
        elif choice == "6":
            account_details(user_id, username)
        elif choice == "7":
            print("Transaction ended!!!")
            break
        else:
            print("Invalid Entry")

    print("***************************************************")
    

# _____________________________________________________________Withdrawer Section_____________________________________

def withdraw(user_id, username):
    try:
        amount = int(input("Enter amount to withdraw: ").strip())
    except ValueError:
        print("Invalid amount")
        return

    if amount <= 0:
        print("Withdrawal amount must be greater than 0")
        return

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        balance = cursor.execute(
            "SELECT initial_balance FROM customers WHERE username = ?",
            (username,)
        ).fetchone()

        if balance is None:
            print("User not found")
            return

        current_balance = balance[0]

        if amount > current_balance:
            print("Insufficient funds")
            return

        new_balance = current_balance - amount

        cursor.execute(
            "UPDATE customers SET initial_balance = ? WHERE username = ?",
            (new_balance, username)
        )
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_id, transaction_type, amount, transaction_date)
            VALUES (?, ?, ?, datetime('now'))
            """, (user_id, "Withdraw", amount))
        print("Connecting to bank server...")
        time.sleep(1)

        print("Verifying account...")
        time.sleep(2)

        print("Processing withdrawal...")
        time.sleep(2)

        print("Dispensing cash...")
        time.sleep(1)
        print(f"Withdrawal successful. New balance: ₦{new_balance}")

    print("***************************************************")

# _____________________________________________________________Deposit Section_____________________________________

def deposit(user_id, username):
    try:
        amount = int(input("Enter amount to deposit: ").strip())
    except ValueError:
        print("Invalid amount")
        return

    if amount <= 0:
        print("Withdrawal amount must be greater than 0")
        return

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        balance = cursor.execute(
            "SELECT initial_balance FROM customers WHERE username = ?",
            (username,)
        ).fetchone()

        if balance is None:
            print("User not found")
            return

        current_balance = balance[0]
        new_balance = current_balance + amount

        cursor.execute(
            "UPDATE customers SET initial_balance = ? WHERE username = ?",
            (new_balance, username)
        )

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_id, transaction_type, amount, transaction_date)
            VALUES (?, ?, ?, datetime('now'))
            """, (user_id, "Depsit", amount))
        print("Connecting to bank server...")
        time.sleep(1)
        print("Processing deposit...")
        time.sleep(2)
        print(f"Deposit successful. New balance: ₦{new_balance}")
    print("***************************************************")

# _____________________________________________________________Transaction History Section_____________________________________


def trans_history(user_id, username):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        transactions = cursor.execute(
            "SELECT transaction_type, amount, transaction_date, recipient_acc FROM transactions WHERE user_id = ?",
            (user_id,)
        ).fetchall()
        for transact in transactions:
            transaction_type, amount, transaction_date, recipient_acc = transact
            result = f"Transaction type: {transaction_type}, amount: {amount}, Date: {transaction_date}, recipient {recipient_acc}."
            print("Connecting to bank server...")
            time.sleep(1)
            print("Processing history...")
            time.sleep(2)
            print(result)
                

# _____________________________________________________________Balance Enquiry Section_____________________________________

def balance_enquiry(user_id, username):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        balance = cursor.execute(
            "SELECT initial_balance FROM customers WHERE username = ?",
            (username,)
        ).fetchone()
        new_balance = balance[0]
        print("Connecting to bank server...")
        time.sleep(1)

        print("Verifying account...")
        time.sleep(2)

        print("Fetching Balance...")
        time.sleep(3)
        print(f"Your account Balance is ₦{new_balance}")

    print("***************************************************")

# _____________________________________________________________Transfer Section_____________________________________

def transfer(user_id, username):
    try:
        account_num = int(input("Enter the receiver account number: "))
        amount = int(input("Enter amount you want to send: "))
    except ValueError:
        print("You Entered an invalid details")
    except TypeError:
        print("You entered a non valid details ")

    if amount <= 0:
        print("Withdrawal amount must be greater than 0")
        return
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        balance = cursor.execute(
            "SELECT initial_balance FROM customers WHERE username = ?",
            (username,)
        ).fetchone()

        if balance is None:
            print("user not found")
            return
        current_balance = balance[0]
        deduct_balance = current_balance - amount

        cursor.execute(
            "UPDATE customers SET initial_balance = ? WHERE username = ?",
            (deduct_balance, username)
        )

        
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        new_balance = cursor.execute(
            "SELECT initial_balance FROM customers WHERE account_number = ?",
            (account_num,)
        ).fetchone()

        added_balance = new_balance[0]
        added_amount = amount + added_balance

        cursor.execute(
            "UPDATE customers SET initial_balance = ? WHERE account_number = ?",
            (added_amount, account_num)
        )

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_id, transaction_type, amount, transaction_date, recipient_acc)
            VALUES (?, ?, ?, datetime('now'), ?)
            """, (user_id, "Transfer", amount, account_num ))
        
    print(f"{amount} sent to {account_num} is successfull!!!!!!")
    

    print("*************************************************************************")

        

# _____________________________________________________________Account Details Section_____________________________________

def account_details(user_id, username):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        account_info = cursor.execute(
            "SELECT full_name, username, initial_balance, account_number FROM customers WHERE username = ?",
            (username,)
        ).fetchone()

        full_name, username, balance, account_number = account_info
    print(f"Your name: {full_name}")
    print(f"Your username: {username}")
    print(f"Your current balance: ₦{balance}")
    print(f"Your account number is: {account_number}")

    print("***************************************************")


start_up()

menu = """
1. Open Account
2. login to Account
3. quit
"""

while True:
    print(menu)
    choice = input("Enter an option: ")

    if choice == "1":
        open_account()
    elif choice == "2":
        login()
    elif choice == "3":
        break
    else:
        print("Invalid choice")
    