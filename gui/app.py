import socket
import threading
import subprocess
import customtkinter as ctk

from crypto.playfair import create_matrix, encrypt, decrypt
from database.db import create_tables, register_user, login_user, save_message, list_messages, delete_message, export_messages_to_txt, list_conversations, create_conversation, save_conversation_message, list_conversation_messages


PORT = 5050

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Şifreli Haberleşme - Giriş")
        self.geometry("900x600")
        self.resizable(True, True)

        create_tables()

        self.title_label = ctk.CTkLabel(
            self,
            text="Şifreli Haberleşme",
            font=("Arial", 24, "bold")
        )
        self.title_label.pack(pady=25)

        self.username_entry = ctk.CTkEntry(
            self,
            placeholder_text="Kullanıcı adı",
            width=260
        )
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(
            self,
            placeholder_text="Şifre",
            show="*",
            width=260
        )
        self.password_entry.pack(pady=10)

        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 13)
        )
        self.status_label.pack(pady=10)

        self.login_button = ctk.CTkButton(
            self,
            text="Giriş Yap",
            width=260,
            command=self.login
        )
        self.login_button.pack(pady=8)

        self.register_button = ctk.CTkButton(
            self,
            text="Kayıt Ol",
            width=260,
            command=self.register
        )
        self.register_button.pack(pady=8)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "" or password == "":
            self.status_label.configure(text="Kullanıcı adı ve şifre boş olamaz.")
            return

        success = login_user(username, password)

        if success:
            #self.status_label.configure(text="Giriş başarılı.")
            self.open_connection_screen(username)
        else:
            self.status_label.configure(text="Kullanıcı adı veya şifre hatalı.")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "" or password == "":
            self.status_label.configure(text="Kullanıcı adı ve şifre boş olamaz.")
            return

        success = register_user(username, password)

        if success:
            self.status_label.configure(text="Kayıt başarılı.")
        else:
            self.status_label.configure(text="Bu kullanıcı adı zaten var.")

    def open_connection_screen(self, username):
        self.clear_screen()

        self.username = username
        self.current_conversation_id = None

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.left_panel = ctk.CTkFrame(self.main_frame, width=300)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))

        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.pack(side="right", fill="both", expand=True)

        user_label = ctk.CTkLabel(
            self.left_panel,
            text=f"Kullanıcı: {username}",
            font=("Arial", 18, "bold")
        )
        user_label.pack(pady=(15, 5))

        my_ip = self.get_tailscale_ip()
        ip_label = ctk.CTkLabel(
            self.left_panel,
            text=f"IP: {my_ip}",
            font=("Arial", 13)
        )
        ip_label.pack(pady=5)

        port_label = ctk.CTkLabel(
            self.left_panel,
            text=f"Port: {PORT}",
            font=("Arial", 13)
        )
        port_label.pack(pady=5)

        self.ip_entry = ctk.CTkEntry(
            self.left_panel,
            placeholder_text="Karşı taraf Tailscale IP",
            width=260
        )
        self.ip_entry.pack(pady=8)

        self.key_entry = ctk.CTkEntry(
            self.left_panel,
            placeholder_text="Şifreleme anahtarı",
            width=260,
            #show="*"
        )
        self.key_entry.pack(pady=8)

        self.connection_status = ctk.CTkLabel(
            self.left_panel,
            text="Bağlantı modu seç",
            wraplength=260
        )
        self.connection_status.pack(pady=10)

        wait_button = ctk.CTkButton(
            self.left_panel,
            text="Bağlantı Bekle",
            width=260,
            command=self.wait_connection
        )
        wait_button.pack(pady=6)

        connect_button = ctk.CTkButton(
            self.left_panel,
            text="Bir Cihaza Bağlan",
            width=260,
            command=self.connect_peer
        )
        connect_button.pack(pady=6)

        old_chats_label = ctk.CTkLabel(
            self.left_panel,
            text="Eski Konuşmalar",
            font=("Arial", 16, "bold")
        )
        old_chats_label.pack(pady=(25, 5))

        self.conversation_frame = ctk.CTkScrollableFrame(
            self.left_panel,
            width=260,
            height=220
        )
        self.conversation_frame.pack(pady=5, fill="both", expand=True)

        self.load_conversations()

        self.chat_title = ctk.CTkLabel(
            self.right_panel,
            text="Sohbet",
            font=("Arial", 22, "bold")
        )
        self.chat_title.pack(pady=15)

        self.chat_box = ctk.CTkTextbox(
            self.right_panel,
            width=520,
            height=390
        )
        self.chat_box.pack(pady=10, padx=15, fill="both", expand=True)
        self.chat_box.configure(state="disabled")

        self.message_entry = ctk.CTkEntry(
            self.right_panel,
            placeholder_text="Mesaj yaz...",
            width=420
        )
        self.message_entry.pack(pady=8)

        send_button = ctk.CTkButton(
            self.right_panel,
            text="Gönder",
            width=200,
            command=self.send_gui_message
        )
        send_button.pack(pady=8)

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def get_tailscale_ip(self):
        try:
            result = subprocess.check_output(
                ["tailscale", "ip", "-4"],
                text=True
            )

            return result.strip()

        except:
            return "Bulunamadı"

    def wait_connection(self):
        key = self.key_entry.get()

        if key == "":
            self.connection_status.configure(text="Şifreleme anahtarı boş olamaz.")
            return

        self.matrix = create_matrix(key)
        self.connection_status.configure(text="Bağlantı bekleniyor...")

        threading.Thread(target=self.start_server_socket, daemon=True).start()

    def start_server_socket(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            server.bind(("0.0.0.0", PORT))
            server.listen()

            self.conn, addr = server.accept()
            
            peer_ip = addr[0]

            self.current_conversation_id = create_conversation(
                self.username,
                peer_ip,
                peer_ip,
                self.key_entry.get()
            )

            self.connection_status.configure(text=f"Bağlandı: {addr[0]}")
            self.chat_title.configure(text=f"Sohbet - {addr[0]}")
            threading.Thread(target=self.receive_gui_messages, daemon=True).start()

        except Exception as e:
            self.connection_status.configure(text=f"Hata: {e}")

    def connect_peer(self):
        key = self.key_entry.get()
        ip = self.ip_entry.get()

        if key == "":
            self.connection_status.configure(
                text="Şifreleme anahtarı boş olamaz."
            )
            return

        if ip == "":
            self.connection_status.configure(
                text="Tailscale IP boş olamaz."
            )
            return

        self.matrix = create_matrix(key)
        
        if self.current_conversation_id is None:
            self.current_conversation_id = create_conversation(
                self.username,
                ip,
                ip,
                key
            )

        threading.Thread(
            target=self.start_client_socket,
            args=(ip,),
            daemon=True
        ).start()
    
    def start_client_socket(self, ip):
        try:
            self.conn = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            self.conn.connect((ip, PORT))

            self.connection_status.configure(
                text="Bağlantı başarılı."
            )

            self.chat_title.configure(text=f"Sohbet - {ip}")
            threading.Thread(target=self.receive_gui_messages, daemon=True).start() 

        except Exception as e:
            self.connection_status.configure(
                text=f"Bağlantı hatası: {e}"
            )

    def open_chat_screen(self):
        self.clear_screen()

        title_label = ctk.CTkLabel(
            self,
            text=f"Sohbet - {self.username}",
            font=("Arial", 22, "bold")
        )
        title_label.pack(pady=10)

        self.chat_box = ctk.CTkTextbox(self, width=360, height=260)
        self.chat_box.pack(pady=10)
        self.chat_box.configure(state="disabled")

        self.message_entry = ctk.CTkEntry(
            self,
            placeholder_text="Mesaj yaz...",
            width=260
        )
        self.message_entry.pack(pady=8)

        send_button = ctk.CTkButton(
            self,
            text="Gönder",
            width=260,
            command=self.send_gui_message
        )
        send_button.pack(pady=8)

        history_button = ctk.CTkButton(
            self,
            text="Geçmişi Göster",
            width=260,
            command=self.show_history
        )
        history_button.pack(pady=5)

        export_button = ctk.CTkButton(
            self,
            text="Sohbeti Dışa Aktar",
            width=260,
            command=self.export_chat
        )
        export_button.pack(pady=5)

        delete_button = ctk.CTkButton(
            self,
            text="Mesaj Sil",
            width=260,
            command=self.delete_message_gui
        )
        delete_button.pack(pady=5)

        threading.Thread(target=self.receive_gui_messages, daemon=True).start()

    def send_gui_message(self):
        msg = self.message_entry.get()

        if msg == "":
            return

        full_msg = f"{self.username}: {msg}"
        encrypted_msg = encrypt(full_msg, self.matrix)

        self.conn.send(encrypted_msg.encode())

        save_message(self.username, msg)

        if self.current_conversation_id is not None:
            save_conversation_message(
                self.current_conversation_id,
                encrypted_msg,
                "out"
            )

        self.add_message_to_chat(f"Ben: {msg}")

    def receive_gui_messages(self):
        while True:
            try:
                data = self.conn.recv(1024)

                if not data:
                    self.add_message_to_chat("Bağlantı kapandı.")
                    break

                decrypted_msg = decrypt(data.decode(), self.matrix)
                self.add_message_to_chat(decrypted_msg)

                if self.current_conversation_id is not None:
                    save_conversation_message(
                        self.current_conversation_id,
                        data.decode(),
                        "in"
                    )

                if ":" in decrypted_msg:
                    sender, message = decrypted_msg.split(":", 1)
                    save_message(sender.strip(), message.strip())
                else:
                    save_message("Karşı taraf", decrypted_msg)

            except Exception as e:
                self.add_message_to_chat(f"Hata: {e}")
                break
    
    def add_message_to_chat(self, message):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", message + "\n")
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def show_history(self):
        list_messages()

    def export_chat(self):
        export_messages_to_txt()
        self.add_message_to_chat("Sohbet geçmişi dışa aktarıldı.")

    def delete_message_gui(self):
        self.add_message_to_chat("Mesaj silme işlemi şimdilik terminalden yapılacak.")

    def load_conversations(self):
        for widget in self.conversation_frame.winfo_children():
            widget.destroy()

        conversations = list_conversations(self.username)

        if not conversations:
            empty_label = ctk.CTkLabel(
                self.conversation_frame,
                text="Kayıtlı konuşma yok."
            )
            empty_label.pack(pady=5)
            return

        for conv_id, peer_ip, peer_name, key_hint, created_at in conversations:
            
            title = peer_name if peer_name else peer_ip

            button_text = title

            if key_hint:
                button_text += f" | key: {key_hint}"

            chat_button = ctk.CTkButton(
                self.conversation_frame,
                text=button_text,
                width=280,
                command=lambda c=conv_id, ip=peer_ip, name=peer_name: self.open_saved_conversation(c, ip, name)
            )
            chat_button.pack(pady=4)

    def open_saved_conversation(self, conversation_id, peer_ip, peer_name):
        self.current_conversation_id = conversation_id

        self.ip_entry.delete(0, "end")
        self.ip_entry.insert(0, peer_ip)

        name_text = peer_name if peer_name else peer_ip

        self.connection_status.configure(
            text=f"Seçilen konuşma: {name_text}. Anahtarı girip geçmişi açabilirsin."
        )

        self.chat_title.configure(text=f"Sohbet - {name_text}")

        self.load_saved_messages()

    def load_saved_messages(self):
        key = self.key_entry.get()

        if key == "":
            self.connection_status.configure(
                text="Geçmişi görmek için önce şifreleme anahtarını gir."
            )
            return

        self.matrix = create_matrix(key)

        self.chat_box.configure(state="normal")
        self.chat_box.delete("1.0", "end")
        self.chat_box.configure(state="disabled")

        messages = list_conversation_messages(self.current_conversation_id)

        if not messages:
            self.add_message_to_chat("Bu konuşmada kayıtlı mesaj yok.")
            return

        for encrypted_message, direction, created_at in messages:
            try:
                decrypted_message = decrypt(encrypted_message, self.matrix)

                if direction == "out":
                    self.add_message_to_chat(f"Ben: {decrypted_message}")
                else:
                    self.add_message_to_chat(decrypted_message)

            except Exception:
                self.add_message_to_chat("[Bu mesaj bu anahtarla çözülemedi]")

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()