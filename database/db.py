import sqlite3
import hashlib


DB_NAME = "secure_chat.db"


def connect_db():
    conn = sqlite3.connect(DB_NAME)
    return conn


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # USERS TABLOSU
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    """)

    # MESSAGES TABLOSU
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()

    password_hash = hash_password(password)

    try:
        cursor.execute("""
        INSERT INTO users (username, password_hash)
        VALUES (?, ?)
        """, (username, password_hash))

        conn.commit()
        print("Kullanıcı başarıyla kaydedildi.")
        conn.close()
        return True

    except sqlite3.IntegrityError:
        print("Bu kullanıcı adı zaten var.")
        conn.close()
        return False


def login_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()

    password_hash = hash_password(password)

    cursor.execute("""
    SELECT * FROM users
    WHERE username = ? AND password_hash = ?
    """, (username, password_hash))

    user = cursor.fetchone()

    conn.close()

    if user:
        print("Giriş başarılı.")
        return True
    else:
        print("Kullanıcı adı veya şifre hatalı.")
        return False


def save_message(sender, message):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO messages (sender, message)
    VALUES (?, ?)
    """, (sender, message))

    conn.commit()
    conn.close()

def list_messages():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, sender, message, created_at
    FROM messages
    ORDER BY created_at ASC
    """)

    messages = cursor.fetchall()

    conn.close()

    if not messages:
        print("Henüz kayıtlı mesaj yok.")
        return

    print("\n--- SOHBET GEÇMİŞİ ---")

    for message_id, sender, message, created_at in messages:
        print(f"{message_id} - [{created_at}] {sender}: {message}")

def delete_message(message_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM messages
    WHERE id = ?
    """, (message_id,))

    conn.commit()
    conn.close()

    print("Mesaj silindi.")

def export_messages_to_txt(filename="chat_export.txt"):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT sender, message, created_at
    FROM messages
    ORDER BY created_at ASC
    """)

    messages = cursor.fetchall()
    conn.close()

    with open(filename, "w", encoding="utf-8") as file:
        file.write("--- SOHBET GEÇMİŞİ ---\n\n")

        for sender, message, created_at in messages:
            file.write(f"[{created_at}] {sender}: {message}\n")

    print(f"Sohbet geçmişi '{filename}' dosyasına aktarıldı.")

if __name__ == "__main__":
    create_tables()

    print("1 - Kayıt Ol")
    print("2 - Giriş Yap")
    print("3 - Mesajları Listele")
    print("4 - Mesaj Sil")

    choice = input("Seçim: ")

    if choice == "1":
        username = input("Kullanıcı adı: ")
        password = input("Şifre: ")
        register_user(username, password)

    elif choice == "2":
        username = input("Kullanıcı adı: ")
        password = input("Şifre: ")
        login_user(username, password)

    elif choice == "3":
        list_messages()

    elif choice == "4":
        list_messages()
        message_id = input("Silinecek mesaj ID: ")
        delete_message(message_id)
    
    else:
        print("Geçersiz seçim.")