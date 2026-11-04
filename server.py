
from socket import *
import threading

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server_socket.bind(('localhost', 8080))
server_socket.listen(5)


# Don't wait forever for a connection
server_socket.settimeout(1.0)

clients = []
clients_lock = threading.Lock()
stop_event = threading.Event()

print("Server running on localhost:8080")


def broadcast(message):
    with clients_lock:
        current_clients = clients.copy()

    for client in current_clients:
        try:
            client.sendall(f"{message}\n".encode())
        except OSError:
            remove_client(client)


def remove_client(client):
    with clients_lock:
        if client in clients:
            clients.remove(client)

    try:
        client.close()
    except OSError:
        pass


def handle_client(client_socket):
    name = "Unknown"

    try:
        client_socket.settimeout(1.0)

        name = client_socket.recv(1024).decode().strip()

        if not name:
            return

        broadcast(f"{name} joined!")
        print(f"Server: {name} connected.")

        while not stop_event.is_set():
            try:
                message = client_socket.recv(1024).decode().strip()

                if not message:
                    break

                broadcast(f"{name}: {message}")
                print(f"Server: {name}: {message}")

            except timeout:
                continue

    except OSError:
        pass

    finally:
        remove_client(client_socket)

        if name != "Unknown" and not stop_event.is_set():
            broadcast(f"{name} left!")
            print(f"Server: {name} disconnected.")


try:
    while not stop_event.is_set():

        try:
            client_socket, addr = server_socket.accept()

            with clients_lock:
                clients.append(client_socket)

            threading.Thread(
                target=handle_client,
                args=(client_socket,),
                daemon=True
            ).start()

        except timeout:
            continue

except KeyboardInterrupt:
    print("\nCtrl + C pressed!")

finally:
    stop_event.set()

    print("Closing connections...")

    server_socket.close()

    with clients_lock:
        connected_clients = clients.copy()
        clients.clear()

    for client in connected_clients:
        try:
            client.shutdown(SHUT_RDWR)
        except OSError:
            pass

        client.close()

    print("Server stopped!")
