import sqlite3
import uuid

def init_database():
    # Creates a connection to the db, will create a db if it does not already exist
    conn = sqlite3.connect("database.db")

    # Create a cursor
    c = conn.cursor()

    # Creates a table first time the code is run
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        email TEXT UNIQUE,
        password TEXT
        );
    """)

    # Create a chat_id with chat_id = str(uuid.uuid4())
    c.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        chat_id TEXT PRIMARY KEY,
        title TEXT,
        sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_upd DATETIME
        );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS chat_logs (
        id INTEGER PRIMARY KEY,
        chat_id TEXT NOT NULL,
        user TEXT NOT NULL,
        sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        message TEXT NOT NULL,
        FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
        );
    """)

    # Commit commands {.execute()} to db 
    conn.commit()

    # Close connection
    conn.close()

# Another function is needed to hash the password
def add_user(user_name: str, email: str, password: str):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO users (user_name, email, password)
        VALUES (?, ?, ?)
        """, (user_name, email, password)
        )
    
    conn.commit()
    conn.close()

def save_msg(chat_id, message):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO chat_logs (chat_id, message) 
    VALUES (?,?)
    """, (chat_id, message)
    )

    conn.commit()
    conn.close()

