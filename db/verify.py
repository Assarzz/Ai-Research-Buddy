import sqlite3

"""def verifyAccount(name, password):
    print(name + " : " + password)
    print(name==password)
    return name == password
    """

def verifyAccount(name,  password):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    SELECT password FROM users WHERE username=?
    """, (name)
    )

    result = c.fetchone()
    conn.close()

    if result is None:
        return False

    return result[0] == password
