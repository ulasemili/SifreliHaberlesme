import socket

HOST = "0.0.0.0"   # herkes bağlanabilsin
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

print(f"[SERVER] Dinleniyor: {HOST}:{PORT}")

conn, addr = server.accept()
print(f"[BAĞLANTI GELDİ] {addr}")

while True:
    data = conn.recv(1024)
    if not data:
        break

    print(f"[MESAJ] {data.decode()}")

    conn.send("Mesaj alındı".encode())

conn.close()