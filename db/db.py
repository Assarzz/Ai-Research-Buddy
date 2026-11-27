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



    c.execute("""
              CREATE TABLE IF NOT EXISTS user_criteria 
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL,
              criteria TEXT NOT NULL,
              FOREIGN KEY (user_id) REFERENCES users(id)
                );
    """)


    c.execute("""
    CREATE TABLE IF NOT EXISTS empirical_standards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        standard TEXT NOT NULL
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

    #creates empirical standards in database
    init_empirical_standards()

    # Commit commands {.execute()} to db
    conn.commit()

    # Close connection
    conn.close()

# Another function is needed to hash the password


def add_user(user_name: str, email: str, password: str) -> bool:
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    try:
        c.execute("""
            INSERT INTO users (user_name, email, password)
            VALUES (?, ?, ?)
            """, (user_name, email, password)
                  )
    except Exception as e:
        print("Error:", e)
        conn.close()
        return False


    conn.commit()
    conn.close()
    return True


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

#temporary fix
def init_empirical_standards():
    standards_lst = [
        "describes the proposed artifact in adequate detail1",
        "justifies the need for, usefulness of, or relevance of the proposed artifact2",
        """EITHER: discusses state-of-art alternatives (and their strengths, weaknesses and limitations)
        OR: explains why no state-of-art alternatives exist
        OR: provides compelling argument that direct comparisons are impractical""",
        """EITHER: empirically compares the artifact to one or more state-of-the-art alternatives
        OR: empirically compares the artifact to one or more state-of-the-art benchmarks
        OR: provides a clear and convincing rationale for why comparative evaluation is impractical""",
        "assumptions (if any) are explicit, plausible and do not contradict each other or the contribution’s goals",
        "uses notation consistently (if any notation is used)",
        "Comprehensiveness of proposed artifact description",
        "Appropriateness of evaluation methods to the nature, goals, and assumptions of the contribution",
        "Relationship of innovativeness to rigorousness: less innovative artifacts require more rigorous evaluations",
        "explains why it is timely to investigate the proposed problem using the proposed method"
        ]
    
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    for i in standards_lst:
        
        try:
            c.execute("""
                INSERT INTO empirical_standards (standard)
                VALUES (?)
                """, (i,)
                    )
        except Exception as e:
            print("Error:", e)
            conn.close()
            return False

    conn.commit()
    conn.close()

    return


if __name__ == "__main__":
    init_database()
