import socket
import threading
import sys

# Constants
MAX_CLIENTS = 10

# Database to store registered clients
registered_clients = set()
all_client_sockets = []
# Function to handle a client
def handle_client(client_socket, client_address):
    username = None # Initialize username, different for each client instance
    all_client_sockets.append(client_socket) # Adds client socket to array
    while True: # Waits
        data = client_socket.recv(1024).decode('utf-8')

        if not data:
            break

        # Parse and handle the received command
        command_parts = data.split()
        command = command_parts[0]

        if command == "JOIN": # JOIN command
            if len(registered_clients) >= MAX_CLIENTS: # Checker in case of max users
                client_socket.send("Too Many Users".encode('utf-8'))
            elif username is None and len(command_parts) == 2 and command_parts[1].isalnum(): # Username is valid
                username = command_parts[1]
                print(f"Connected with {client_address} ")
                #print(f"{username} Joined the Chatroom ")
                
                # after new client join, get the last element of client list
                client = all_client_sockets[-1]
                client.send(f"welcome {username} to the server".encode('utf-8'))
                print(f"{username} Joined the Chatroom")
                
                #for client in all_client_sockets:
                    #client.send(f"welcome {username} to the server".encode('utf-8'))
                    #print(f"{username} Joined the Chatroom")
                    
                registered_clients.add(username)
            else:
                client_socket.send("Join Error".encode('utf-8')) # Username invalid

        elif command == "LIST": # LIST command
            if username:
                client_socket.send(",".join(registered_clients).encode('utf-8')) # Sends user list,
                # taken from the registered_client set
            else:
                client_socket.send("Not Registered".encode('utf-8'))

        elif command == "MESG": # MESG command
            if username and len(command_parts) >= 3 and command_parts[1] in registered_clients:  # Checker to ensure
                # formatting is correct and recipient exists
                recipient = command_parts[1]
                message = " ".join(command_parts[2:]) # Parses rest of message to
                print(f"{username} to {recipient}: {message}")
                # Implement logic to send the message to the recipient
                num = 0
                for i in registered_clients: # Iterates through registered clients to find correct user target
                    if i == recipient:
                        num = num + 1
                for client in all_client_sockets: # Sends notification to every user
                    if client == all_client_sockets[num-1]:
                        client.send(f"{username} has send {recipient} a message: {message}".encode('utf-8'))
            else:
                client_socket.send("Unknown Recipient".encode('utf-8'))

        elif command == "BCST":
            if username and len(command_parts) >= 2: # Checker to ensure command is proper
                message = " ".join(command_parts[1:])
                print(f"{username} (Broadcast): {message}")
                for client in all_client_sockets:
                    client.send(f"{username} sent a broadcast message: {message}".encode('utf-8')) # sends the message
                    # to all users

                # client_socket.sendall(f"{username} sent to all: {message}".encode('utf-8'))
                # Implement logic to broadcast the message to all clients except the sender
            else:
                client_socket.send("Invalid BCST Request".encode('utf-8'))

        elif command == "QUIT": # breaks the loop for client on quit command
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
    if len(sys.argv) != 2: # Checker to make sure initial call is formatted correctly
        print("Usage: python3 server.py <svr_port>")
        sys.exit(1)

    host = '0.0.0.0'
    port = int(sys.argv[1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP socket
    server_socket.bind((host, port))
    server_socket.listen()

    print("The Chat Server Started")

    while True: # Mutlithreaded client functionality
        client_socket, client_address = server_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_handler.start()

if __name__ == "__main__":
    main()
