import socket
import threading
from crypto.playfair import create_matrix, encrypt, decrypt
from database.db import create_tables, register_user, login_user , save_message , list_messages , delete_message , export_messages_to_txt

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
        else:
            return None

    elif choice == "2":
        success = login_user(username, password)

        if success:
            return username
        else:
            return None

    else:
        print("Geçersiz seçim.")
        return None


username = auth_menu()

if username is None:
    print("Giriş yapılamadı. Program kapatılıyor.")
    exit()

SERVER_IP = "100.87.168.123"
PORT = 5050

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))
print("[BAĞLANDI]")

key = input("Şifreleme Anahtarı: ")
matrix = create_matrix(key)


# 🔹 Mesaj alma
def receive_messages():
    while True:
        try:
            data = client.recv(1024)
            if not data:
                break
            decrypted_msg = decrypt(data.decode(), matrix)

            print(f"\n\n[GELEN MESAJ]: {decrypted_msg}")
            print("Mesajınız: ", end="", flush=True)

            if ":" in decrypted_msg:
                sender, message = decrypted_msg.split(":", 1)
                save_message(sender.strip(), message.strip())
            else:
                save_message("Karşı taraf", decrypted_msg)
        except:
            break


# 🔹 Mesaj gönderme
def send_messages():

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
            client.send(encrypted_msg.encode())
            save_message(username, msg)

        except Exception as e:
            print("HATA:", e)
            print("Bağlantı Koptu!")
            break


threading.Thread(target=receive_messages).start()
threading.Thread(target=send_messages).start()