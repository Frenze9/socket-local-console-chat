from socket import *
import threading
import time

# Connection function
def connect():
    name = input("Enter your name: ").strip()

    while True:
        sock = socket(AF_INET, SOCK_STREAM)

        try:
            sock.connect(('localhost', 8080))
            sock.sendall(name.encode())

            print(f"Connected to server as {name}!")
            return sock

        except OSError as e:
            print(f"Connection failed: {e}")
            sock.close()
            print("Retrying in 1 second...")
            time.sleep(1)


client_socket = connect()

stop_event = threading.Event()


# Sending messages
def send_message():
    while not stop_event.is_set():
        try:
            msg = input()

            if msg.lower() == 'exit':
                stop_event.set()
                client_socket.shutdown(SHUT_WR)
                break

            if msg:
                client_socket.sendall(msg.encode())

        except (OSError, EOFError):
            stop_event.set()
            break


# Receiving messages
def receive_messages():
    while not stop_event.is_set():
        try:
            message = client_socket.recv(1024)

            if not message:
                print("\nServer disconnected.")
                stop_event.set()
                break

            print(message.decode().strip())

        except OSError:
            if not stop_event.is_set():
                print("\nConnection lost.")

            stop_event.set()
            break


# Start threads
send_thread = threading.Thread(
    target=send_message,
    daemon=True
)

receive_thread = threading.Thread(
    target=receive_messages,
    daemon=True
)

send_thread.start()
receive_thread.start()

try:
    receive_thread.join()

except KeyboardInterrupt:
    print("\nDisconnecting...")

finally:
    stop_event.set()
    client_socket.close()
    print("Client stopped.")
