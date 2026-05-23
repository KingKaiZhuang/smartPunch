import sqlitecloud
from env_config import get_required_env

def test_db():
    conn = sqlitecloud.connect(get_required_env("SQLITECLOUD_URL"))
    
    # Check what parameters it accepts
    try:
        cursor = conn.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
        print("Created table")
        
        # Test parameter substitution: does it accept ? or %s
        try:
            conn.execute("INSERT INTO test_table (name) VALUES (?)", ("test_user",))
            print("Accepts ?")
        except Exception as e:
            print("Failed ?:", e)
            
        try:
            conn.execute("INSERT INTO test_table (name) VALUES (%s)", ("test_user2",))
            print("Accepts %s")
        except Exception as e:
            print("Failed %s:", e)
            
        cursor = conn.execute("SELECT * FROM test_table")
        print("fetchall without row_factory:")
        rows = cursor.fetchall()
        for r in rows:
            print(r)
            
        # Try returning dictionaries
        try:
            def dict_factory(cursor, row):
                d = {}
                for idx, col in enumerate(cursor.description):
                    d[col[0]] = row[idx]
                return d
            
            conn.row_factory = dict_factory
            cursor = conn.execute("SELECT * FROM test_table LIMIT 1")
            print("fetchone with dict_factory:", cursor.fetchone())
        except Exception as e:
            print("Failed setting row_factory:", e)
            
    finally:
        # Cleanup
        conn.execute("DROP TABLE IF EXISTS test_table")
        conn.close()

if __name__ == "__main__":
    test_db()
