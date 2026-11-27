import sqlite3

"""def verifyAccount(name, password):
    print(name + " : " + password)
    print(name==password)
    return name == password
    """

def verifyAccount(name,  password):
    account_dict = {
        "account_validity": False,
        "user_ID": "",
    }
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    SELECT password FROM users WHERE user_name=?
    """, (name,)
    )

    stored_password = c.fetchone()
    
    c.execute("""
    SELECT id FROM users WHERE user_name=? AND password =?
    """, (name,password)
    )
    user_ID = c.fetchone()
    conn.close()

    if stored_password is None:
        return False
    account_dict["account_validity"] = stored_password[0] == password
    account_dict["user_ID"] = user_ID

    return account_dict

if __name__ == "__main__":
    res = verifyAccount("Walter White", "1234")
    print(res)
