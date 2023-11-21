import socket
import sys

def send_request(sock, request):
    sock.sendall(request.encode('utf-8'))

def receive_response(sock):
    data = sock.recv(1024)
    return data.decode('utf-8')

def main():
    if len(sys.argv) != 3:
        print("Usage: python client.py <hostname> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))

            # Loop until a valid JOIN command is provided
            while True:
                # Issue JOIN request
                join_command = input("Enter 'JOIN' followed by your username: ")
                if join_command.upper().startswith("JOIN "):
                    send_request(s, join_command)
                    response = receive_response(s)
                    print(response)
                    if response != "Username already taken. Please choose another.":
                        break
                    # Break out of the loop if the JOIN command is valid

                else:
                    print("Invalid command. Please enter 'JOIN' followed by your username (JOIN {username})")

            while True:
                # Handle user input
                user_input = input("Enter your message or type 'QUIT' to exit: ")
                if user_input.upper() == "QUIT":
                    send_request(s, "QUIT")
                    break

                # Send the entire input string to the server
                send_request(s, user_input)

                # Receive and print server response
                response = receive_response(s)
                print(response)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()