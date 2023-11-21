import socket
import sys
import threading

# Constants
MAX_CLIENTS = 10
REGISTERED_CLIENTS = set()
lock = threading.Lock()

# Function to handle a client in a separate thread
def handle_client(client_socket, client_address):
    try:
        print(f"Connection from {client_address}")

        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            request = data.decode('utf-8')
            print(f"Received from {client_address}: {request}")

            if request.startswith("JOIN"):
                requested_username = request.split()[1]
                with lock:
                    if requested_username not in REGISTERED_CLIENTS:
                        REGISTERED_CLIENTS.add(requested_username)
                        response = "Joined successfully!"
                    else:
                        response = "Username already taken. Please choose another."

            elif request == "LIST":
                with lock:
                    response = "\n".join(REGISTERED_CLIENTS)

            elif request.startswith("MESG"):
                parts = request.split()
                target_username = parts[1]
                if target_username in REGISTERED_CLIENTS:
                    message = ' '.join(parts[2:])
                    response = f"Message from {requested_username}: {message}"
                    client_socket.sendall(response.encode('utf-8'))
                    continue  # Skip broadcasting
                else:
                    response = f"Unknown recipient: {target_username}"

            elif request.startswith("BCST"):
                message = ' '.join(request.split()[1:])
                with lock:
                    response = f"Broadcast from {requested_username}: {message}"

            elif request == "QUIT":
                with lock:
                    response = "Goodbye!"
                    break

            else:
                response = "Unknown message."

            client_socket.sendall(response.encode('utf-8'))

        with lock:
            REGISTERED_CLIENTS.remove(requested_username)

    except Exception as e:
        print(f"Error handling client {client_address}: {e}")

    finally:
        print(f"Connection closed from {client_address}")
        client_socket.close()

# Main server function
def main():
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
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_handler.start()

    except Exception as e:
        print(f"Error in the main server loop: {e}")

    finally:
        server_socket.close()

# Entry point
if __name__ == "__main__":
    main()