# Sifreli Haberlesme - Peer-to-Peer Mesajlaşma Uygulaması
# server & client kodları tek bir dosyada, kullanıcı giriş yaparken seçim yaparak server veya client olarak çalışacak şekilde düzenlendi.
# yani kullanıcı isterse önce server'ı başlatıp ardından client'ı başlatabilir veya tam tersi şekilde çalıştırabilir.
import socket
import threading

from crypto.playfair import create_matrix, encrypt, decrypt
from database.db import (
    create_tables,
    register_user,
    login_user,
    save_message,
    list_messages,
    delete_message,
    export_messages_to_txt
)


PORT = 5050


def auth_menu():
    create_tables()

    print("1 - Kayıt Ol")
    print("2 - Giriş Yap")

    choice = input("Seçim: ")

    username = input("Kullanıcı adı: ")
    password = input("Şifre: ")

    if choice == "1":
        success = register_user(username, password)
        if success:
            return username
        return None

    elif choice == "2":
        success = login_user(username, password)
        if success:
            return username
        return None

    else:
        print("Geçersiz seçim.")
        return None


def wait_for_connection():
    HOST = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[BEKLENİYOR] Bağlantı bekleniyor: {HOST}:{PORT}")

    conn, addr = server.accept()
    print(f"[BAĞLANDI] {addr}")

    return conn


def connect_to_peer():
    server_ip = input("Bağlanılacak Tailscale IP: ")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((server_ip, PORT))

        print("[BAĞLANDI]")
        return client

    except ConnectionRefusedError:
        print("\n[HATA]")
        print("Karşı kullanıcı çevrimdışı olabilir.")
        print("Bağlantı kurulamadı.")

        return None

    except Exception as e:
        print("\n[HATA]")
        print(e)

        return None


def receive_messages(conn, matrix):
    while True:
        try:
            data = conn.recv(1024)

            if not data:
                print("Bağlantı kapandı.")
                break

            decrypted_msg = decrypt(data.decode(), matrix)

            print(f"\n\n[GELEN MESAJ]: {decrypted_msg}")
            print("Mesajınız: ", end="", flush=True)

            if ":" in decrypted_msg:
                sender, message = decrypted_msg.split(":", 1)
                save_message(sender.strip(), message.strip())
            else:
                save_message("Karşı taraf", decrypted_msg)

        except Exception as e:
            print("HATA:", e)
            break


def send_messages(conn, matrix, username):
    while True:
        try:
            msg = input("Mesajınız: ")

            if msg == "/sil":
                list_messages()
                message_id = input("Silinecek mesaj ID: ")
                delete_message(message_id)
                continue

            if msg == "/gecmis":
                list_messages()
                continue

            if msg == "/export":
                export_messages_to_txt()
                continue

            full_msg = f"{username}: {msg}"

            encrypted_msg = encrypt(full_msg, matrix)
            conn.send(encrypted_msg.encode())

            save_message(username, msg)

        except Exception as e:
            print("HATA:", e)
            print("Bağlantı Koptu!")
            break


def main():
    username = auth_menu()

    if username is None:
        print("Giriş yapılamadı. Program kapatılıyor.")
        return

    key = input("Şifreleme Anahtarı: ")
    matrix = create_matrix(key)

    print("\nBağlantı modu seç:")
    print("1 - Bağlantı Bekle")
    print("2 - Bir Cihaza Bağlan")

    mode = input("Seçim: ")

    if mode == "1":
        conn = wait_for_connection()

    elif mode == "2":
        conn = connect_to_peer()
        
        if conn is None:
            return

    else:
        print("Geçersiz seçim.")
        return

    threading.Thread(target=receive_messages, args=(conn, matrix), daemon=True).start()
    send_messages(conn, matrix, username)


if __name__ == "__main__":
    main()