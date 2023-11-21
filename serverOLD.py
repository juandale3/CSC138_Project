import socket
import sys
import threading
import queue  # Add this import statement

# Constants
MAX_CLIENTS = 10
REGISTERED_CLIENTS = set()
lock = threading.Lock()
client_data = {}


def get_or_create_client(thread):
    with lock:
        if thread not in client_data:
            client_data[thread] = ClientWrapper(None)
        return client_data[thread]


# Queue to hold messages for broadcasting
broadcast_queue = queue.Queue()


# Client wrapper to store separate usernames
class ClientWrapper:
    def __init__(self, socket, username=None):
        self.socket = socket
        self.request_username = username


# Function to handle broadcasting in a separate thread
def handle_broadcast():
    while True:
        message = broadcast_queue.get()
        with lock:
            sent_clients = set()

            for thread, client in client_data.items():
                if client.socket and client not in sent_clients:
                    client.socket.sendall(message.encode('utf-8'))
                    sent_clients.add(client)

            broadcast_queue.task_done()


# Start the broadcasting thread
broadcast_thread = threading.Thread(target=handle_broadcast)
broadcast_thread.start()


# Function to send a message to all clients
def send_message_to_all_clients(message):
    broadcast_queue.put(message)


# Function to send a message to a specific client
def send_message_to_client(target_username, message, broadcast=False):
    with lock:
        for thread, client in client_data.items():
            if client.request_username == target_username or broadcast:
                if client.socket:
                    client.socket.sendall(message.encode('utf-8'))


# Function to handle a client in a separate thread
def handle_client(client_socket, client_address):
    try:
        print(f"Connection from {client_address}")

        current_thread = threading.current_thread()
        client = ClientWrapper(client_socket)  # Create a new ClientWrapper for each thread
        client_data[current_thread] = client

        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            request = data.decode('utf-8')
            print(f"Received from {client_address}: {request}")

            if request.startswith("JOIN"):
                username_attempt = request.split()[1]
                with lock:
                    if username_attempt not in REGISTERED_CLIENTS:
                        REGISTERED_CLIENTS.add(username_attempt)
                        client.request_username = username_attempt
                        response = "Joined successfully!"
                    else:
                        response = "Username already taken. Please choose another."

            elif request == "LIST":
                with lock:
                    response = "\n".join(REGISTERED_CLIENTS)

            elif request.startswith("MESG"):
                try:
                    sender_username = client.request_username
                    parts = request.split()
                    target_username = parts[1]
                    if target_username in REGISTERED_CLIENTS:
                        message = ' '.join(parts[2:])
                        response = f"Message from {sender_username}: {message}"
                        send_message_to_client(target_username, response, False)
                        continue  # Skip broadcasting
                    else:
                        response = f"Unknown recipient: {target_username}"
                except Exception as e:
                    print(f"Unknown Format")


            elif request.startswith("BCST"):
                try:
                    message = ' '.join(request.split()[1:])
                    with lock:
                        response = f"Broadcast from {client.request_username}: {message}"
                        broadcast_queue.put(response)
                except Exception as e:
                    print(f"Unknown Format")


            elif request == "QUIT":
                with lock:
                    response = "Goodbye!"
                    break

            else:
                response = "Unknown message."

            client_socket.sendall(response.encode('utf-8'))

    except Exception as e:
        print(f"Error handling client {client_address}: {e}")


    finally:
        with lock:
            if client.request_username in REGISTERED_CLIENTS:
                REGISTERED_CLIENTS.remove(client.request_username)
            del client_data[threading.current_thread()]  # Remove client data

        print(f"Connection closed from {client_address}")

        client_socket.close()


# Main server function
def main():
    global client_address
    if len(sys.argv) != 2:
        print("Usage: python3 server.py <port>")
        sys.exit(1)
    port = int(sys.argv[1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(10)  # Allow up to 10 clients to queue up

    print(f"Server listening on port {port}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()

            client = ClientWrapper(client_socket)
            client_data[threading.Thread(target=handle_client, args=(client_socket, client_address))] = client

            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_handler.start()

    except Exception as e:
        print(f"Error in the main server loop: {e}")

    finally:
        print(f"Connection closed from {client_address}")
        server_socket.close()


# Entry point
if __name__ == "__main__":
    main()
