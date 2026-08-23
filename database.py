import sqlite3

def get_db():
    conn = sqlite3.connect("pyq.db", check_same_thread=False)
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    # Table to store PYQs
    c.execute("""
    CREATE TABLE IF NOT EXISTS pyqs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        sub_category TEXT,
        year TEXT,
        file_id TEXT,
        file_name TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_pyq(category, sub_category, year, file_id, file_name):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO pyqs (category, sub_category, year, file_id, file_name) VALUES (?,?,?,?,?)",
              (category, sub_category, year, file_id, file_name))
    conn.commit()
    conn.close()

def get_sub_categories(category):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT DISTINCT sub_category FROM pyqs WHERE category=?", (category,))
    rows = [r[0] for r in c.fetchall()]
    conn.close()
    return rows

def get_years(category, sub_category):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT DISTINCT year FROM pyqs WHERE category=? AND sub_category=? ORDER BY year DESC", (category, sub_category))
    rows = [r[0] for r in c.fetchall()]
    conn.close()
    return rows

def get_files(category, sub_category, year):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT file_id, file_name FROM pyqs WHERE category=? AND sub_category=? AND year=?", (category, sub_category, year))
    rows = c.fetchall()
    conn.close()
    return rows

# Initialize on import
init_db()