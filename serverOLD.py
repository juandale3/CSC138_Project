import socket
import threading
import sys

# Constants
MAX_CLIENTS = 10

# Database to store registered clients
registered_clients = set()

# Function to handle a client
def handle_client(client_socket, client_address):
    username = None

    while True:
        data = client_socket.recv(1024).decode('utf-8')

        if not data:
            break

        # Parse and handle the received command
        command_parts = data.split()
        command = command_parts[0]

        if command == "JOIN":
            if len(registered_clients) >= MAX_CLIENTS:
                client_socket.send("Too Many Users".encode('utf-8'))
            elif username is None and len(command_parts) == 2 and command_parts[1].isalnum():
                username = command_parts[1]
                registered_clients.add(username)
                print(f"{username} Joined the Chatroom")
                client_socket.send("Welcome".encode('utf-8'))
            elif username is not None:
                client_socket.send("Already Registered".encode('utf-8'))
            else:
                client_socket.send("Invalid JOIN Request".encode('utf-8'))

        elif command == "LIST":
            if username:
                client_socket.send(",".join(registered_clients).encode('utf-8'))
            else:
                client_socket.send("Not Registered".encode('utf-8'))

        elif command == "MESG":
            if username and len(command_parts) >= 3 and command_parts[1] in registered_clients:
                recipient = command_parts[1]
                message = " ".join(command_parts[2:])
                print(f"{username} to {recipient}: {message}")
                # Implement logic to send the message to the recipient
            elif username is None:
                client_socket.send("Not Registered".encode('utf-8'))
            else:
                client_socket.send("Unknown Recipient".encode('utf-8'))

        elif command == "BCST":
            if username and len(command_parts) >= 2:
                message = " ".join(command_parts[1:])
                print(f"{username} (Broadcast): {message}")
                client_socket.sendall(f"{username} sent to all: {message}".encode('utf-8'))
                # Implement logic to broadcast the message to all clients except the sender
            elif username is None:
                client_socket.send("Not Registered".encode('utf-8'))
            else:
                client_socket.send("Invalid BCST Request".encode('utf-8'))

        elif command == "QUIT":
            break

        else:
            client_socket.send("Unknown Message".encode('utf-8'))

    # Cleanup when client disconnects
    if username:
        registered_clients.remove(username)
        print(f"{username} Left the Chatroom")
    client_socket.close()

# Main function to start the server
def main():
    if len(sys.argv) != 2:
        print("Usage: python3 server.py <svr_port>")
        sys.exit(1)

    host = '0.0.0.0'
    port = int(sys.argv[1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    print("The Chat Server Started")

    while True:
        client_socket, client_address = server_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_handler.start()

if __name__ == "__main__":
    main()