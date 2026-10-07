import sqlite3

def init_database():
    # Creates a connection to the db, will create a db if it does not already exist
    conn = sqlite3.connect("database.db")

    # Create a cursor
    c = conn.cursor()

    # Datatypes:
    # NULL 
    # INTEGER
    # REAL (decimal)
    # TEXT
    # BLOB (images, mp3 etc.)

    # Creates a table first time the code is run
    c.exectue("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        email TEXT UNIQUE,
        password TEXT
        );
    """)

    # Commit commands {.execute()} to db 
    conn.commit()

    # Close connection
    conn.close()

# Another function is needed to encrypt the password
def add_user(user_name: str, email: str, password: str):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute(f"""
        INSERT INTO users (user_name, email)
        VALUES ({user_name}, {email}, {password});
        """)
    
    conn.commit()
    conn.close()
