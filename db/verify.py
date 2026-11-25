import sqlite3
import bcrypt

def verifyAccount(name,  password):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    SELECT password FROM users WHERE user_name=?
    """, (name,)
    )

    result = c.fetchone()
    conn.close()

    if result is None:
        return False

    stored_hash = result[0]

    return bcrypt.checkpw(
        password.encode("utf-8"),
        stored_hash.encode("utf-8")
    )
