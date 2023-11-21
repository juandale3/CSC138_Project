# 138 Project server.py
import socket
import threading

# Constants
MAX_CLIENTS = 10

# Data structures to store registered clients
registered_clients = {}
lock = threading.Lock()

# Function to handle client requests
def handle_client(client_socket, client_address):
    print(f"Connection from {client_address}")

    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            
            # Split the command and username
            command, *args = data.split()

            if command == "JOIN":
                handle_join(client_socket, args[0])
            elif command == "LIST":
                handle_list(client_socket)
            else:
                print(f"Unknown command from {client_address}: {command}")

        except Exception as e:
            print(f"Error handling {client_address}: {e}")
            break

    # Remove client from registered clients
    with lock:
        if client_socket.fileno() in registered_clients:
            del registered_clients[client_socket.fileno()]

    print(f"Connection from {client_address} closed")
    client_socket.close()

# Function to handle JOIN command
def handle_join(client_socket, username):
    with lock:
        if len(registered_clients) >= MAX_CLIENTS:
            print(f"Too many users. {username} cannot join.")
            client_socket.send("Too Many Users\n".encode('utf-8'))
        elif client_socket.fileno() in registered_clients:
            print(f"{username} is already registered.")
            client_socket.send(f"{username} is already registered.\n".encode('utf-8'))
        else:
            registered_clients[client_socket.fileno()] = username
            print(f"{username} joined the server.")
            client_socket.send(f"Joined as {username}\n".encode('utf-8'))

# Function to handle LIST command
def handle_list(client_socket):
    with lock:
        if client_socket.fileno() in registered_clients:
            client_socket.send("\n".join(registered_clients.values()).encode('utf-8'))
        else:
            print("Unauthorized LIST request from non-registered client.")

# Main server function
def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)

    print(f"Server listening on port {port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print("accepted connection")
        #client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
        data = client_socket.recv(1024)
        if data:
            print("reveived message:", {data.decode()})
        client_socket.close()
        #client_handler.start()

# Entry point
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 server.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    start_server(port)
