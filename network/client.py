import socket

SERVER_IP = "127.0.0.1"  # kendi bilgisayarın
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))

print("[BAĞLANDI]")

while True:
    msg = input("Mesaj yaz: ")

    client.send(msg.encode())

    data = client.recv(1024)
    print(f"[SERVER] {data.decode()}")