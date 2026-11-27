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
    
    j = 0
    for i in result:
        result[j] = i[0]
        j = j + 1

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
