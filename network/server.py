import socket
import threading

HOST = "127.0.0.1"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"[SERVER] Dinleniyor: {HOST}:{PORT}")

conn, addr = server.accept()
print(f"[BAĞLANDI] {addr}")


# 🔹 Mesaj alma thread'i
def receive_messages():
    while True:
        try:
            data = conn.recv(1024)
            if not data: 
                break
            print(f"\n[CLIENT]: {data.decode()}")
        except:
            break


# 🔹 Mesaj gönderme thread'i
def send_messages():
    while True:
        msg = input()
        conn.send(msg.encode())

# Thread başlat
threading.Thread(target=receive_messages).start()
threading.Thread(target=send_messages).start()