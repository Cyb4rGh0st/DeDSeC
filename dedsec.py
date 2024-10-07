import socket
import socks  # Nowa biblioteka do obsługi tunelowania
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
import threading
import base64

# Konfiguracja tunelu SOCKS przez I2P
def configure_socks_proxy():
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 4444)  # Adres i port lokalnego tunelu SOCKS
    socket.socket = socks.socksocket

# Funkcja do szyfrowania wiadomości
def encrypt_message(message, recipient_public_key, sender_private_key):
    box = Box(sender_private_key, recipient_public_key)
    encrypted = box.encrypt(message.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')

# Funkcja do odszyfrowania wiadomości
def decrypt_message(encrypted_message, recipient_private_key, sender_public_key):
    box = Box(recipient_private_key, sender_public_key)
    decoded_message = base64.b64decode(encrypted_message)
    decrypted = box.decrypt(decoded_message).decode('utf-8')
    return decrypted

# Funkcja do nasłuchiwania wiadomości
def listen_for_messages(sock, private_key, peer_public_key):
    while True:
        encrypted_message = sock.recv(1024).decode('utf-8')
        print(f"Otrzymana zaszyfrowana wiadomość: {encrypted_message}")
        try:
            message = decrypt_message(encrypted_message, private_key, peer_public_key)
            print(f"Odszyfrowana wiadomość: {message}")
        except Exception as e:
            print(f"Błąd podczas deszyfrowania: {e}")

# Funkcja do wysyłania wiadomości
def send_message(sock, message, recipient_public_key, sender_private_key):
    encrypted_message = encrypt_message(message, recipient_public_key, sender_private_key)
    sock.sendall(encrypted_message.encode('utf-8'))

# Funkcja główna - łączenie użytkowników P2P
def start_communicator(is_server, ip, port, peer_public_key=None):
    private_key, public_key = generate_keys()

    if is_server:
        # Tryb serwera
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip, port))
        server_socket.listen(1)
        print(f"Serwer nasłuchuje na {ip}:{port}...")
        conn, addr = server_socket.accept()
        print(f"Połączono z {addr}")

        # Odbieranie wiadomości
        threading.Thread(target=listen_for_messages, args=(conn, private_key, peer_public_key)).start()

        # Wysyłanie wiadomości
        while True:
            message = input("Wpisz wiadomość: ")
            send_message(conn, message, peer_public_key, private_key)

    else:
        # Tryb klienta
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        print(f"Połączono z {ip}:{port}")

        # Odbieranie wiadomości
        threading.Thread(target=listen_for_messages, args=(client_socket, private_key, peer_public_key)).start()

        # Wysyłanie wiadomości
        while True:
            message = input("Wpisz wiadomość: ")
            send_message(client_socket, message, peer_public_key, private_key)

# Główna funkcja uruchomieniowa
if __name__ == "__main__":
    configure_socks_proxy()  # Konfiguracja tunelu SOCKS przez I2P
    
    mode = input("Tryb [server/client]: ")
    ip = input("Adres IP: ")
    port = int(input("Port: "))

    if mode == "server":
        start_communicator(True, ip, port)

    elif mode == "client":
        peer_public_key_hex = input("Podaj publiczny klucz serwera (hex): ")
        peer_public_key = PublicKey(bytes.fromhex(peer_public_key_hex))
        start_communicator(False, ip, port, peer_public_key)