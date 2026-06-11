import socket
import threading
from crypto.playfair import create_matrix, encrypt, decrypt
from database.db import save_message, create_tables

HOST = "0.0.0.0"
PORT = 5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
server.bind((HOST, PORT))
server.listen()

print(f"[SERVER] Dinleniyor: {HOST}:{PORT}")

conn, addr = server.accept()
print(f"[BAĞLANDI] {addr}")

create_tables()

key = input("Şifreleme Anahtarı: ")
matrix = create_matrix(key)

# 🔹 Mesaj alma thread'i
def receive_messages():
    while True:
        try:
            data = conn.recv(1024)
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
        except Exception as e:
            print("HATA:", e)
            break


# 🔹 Mesaj gönderme thread'i
def send_messages():
    name = input("ADINIZ : ")

    while True:
        try:
            msg = input("Mesajınız: ")

            full_msg = f"{name}: {msg}"

            encrypted_msg = encrypt(full_msg, matrix)
            conn.send(encrypted_msg.encode())
            save_message(name, msg)

        except Exception as e:
            print("HATA:", e)
            print("Bağlantı Koptu!")
            break

# Thread başlat
threading.Thread(target=receive_messages).start()
threading.Thread(target=send_messages).start()