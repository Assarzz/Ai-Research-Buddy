import sqlite3




def fetch_criteria(user_ID):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    SELECT criteria FROM user_criteria WHERE user_id=?
    """, (user_ID,)
        )
    
    result = c.fetchall()
    conn.close()
    
    return result

def add_criteria(user_id,criteria):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    try:
        c.execute("""
            INSERT INTO user_criteria (user_id, criteria)
            VALUES (?, ?)
            """, (user_id, criteria)
                  )
    except Exception as e:
        print("Error:", e)
        conn.close()
        return False
    conn.commit()
    conn.close()
    return True


if __name__ == "__main__":
    name = "Walter White"

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    SELECT id FROM users WHERE user_name=?
    """, (name,)
    )
    result = c.fetchone()
    
    add_criteria(result[0],"Is abstract good?")
    add_criteria(result[0],"Is abstract bad?")
    res = fetch_criteria(result[0])
    print(res)
    print("-----------------------------------------------")
    c.execute("""SELECT * FROM user_criteria""")
    print(c.fetchall())
    conn.close()
    