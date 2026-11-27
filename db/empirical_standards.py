import sqlite3

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
