import sqlite3

def init_db():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS blocked_users (user_id INTEGER PRIMARY KEY)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS messages (user_id INTEGER, message TEXT)""")
    conn.commit()
    conn.close()

def is_blocked(user_id):
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM blocked_users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    conn.close()
    return result is not None

def block_user(user_id):
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO blocked_users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def save_message(user_id, message):
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (user_id, message) VALUES (?, ?)", (user_id, message))
    conn.commit()
    conn.close()
