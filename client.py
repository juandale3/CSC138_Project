import socket
import sys
import threading

def receive_messages(socket):
    try:
        while True:
            data = socket.recv(1024)
            if not data:
                break
            print(data.decode('utf-8'))
    except Exception as e:
        print(f"Error receiving messages: {e}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 client.py <hostname> <port>")
        sys.exit(1)

    hostname = sys.argv[1]
    port = int(sys.argv[2])

    try:
        # Connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((hostname, port))

        # Loop until a valid JOIN command is provided
        while True:
            # Get user input for the username
            username = input("Enter JOIN <username>: ")

            # Validate and send JOIN request with the chosen username
            if username.startswith("JOIN "):
                client_socket.sendall(username.encode('utf-8'))
                break
            else:
                print("Invalid format. Please start with JOIN <username>.")

        # Start a separate thread to receive messages from the server
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()

        while True:
            # Get user input for commands
            command = input("Enter command (LIST, MESG <username> <message>, BCST <message>, QUIT): ")

            if command == "QUIT":
                client_socket.sendall(command.encode('utf-8'))
                break

            # Send the user command to the server
            client_socket.sendall(command.encode('utf-8'))

    except Exception as e:
        print(f"Error in the main client loop: {e}")

    finally:
        print("Connection closed.")
        client_socket.close()

if __name__ == "__main__":
    main()