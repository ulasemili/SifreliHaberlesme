import socket
import threading

SERVER_IP = "127.0.0.1"
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))

print("[BAĞLANDI]")


# 🔹 Mesaj alma
def receive_messages():
    while True:
        try:
            data = client.recv(1024)
            if not data:
                break
            print(f"\n[SERVER]: {data.decode()}")
        except:
            break


# 🔹 Mesaj gönderme
def send_messages():
    while True:
        try:
            name = input("ADINIZ : ")
            msg = input()
            client.send(f"{name} : {msg}".encode())
        except:
                 print("Bağlantı Koptu!")
                 break


threading.Thread(target=receive_messages).start()
threading.Thread(target=send_messages).start()