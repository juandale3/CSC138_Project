import socket
import sys
import threading
import select
from queue import Queue


def send_request(sock, request):
    sock.sendall(request.encode('utf-8'))


def receive_response(sock, response_queue):
    while True:
        ready, _, _ = select.select([sock], [], [], 0.1)
        if ready:
            data = sock.recv(1024)
            if not data:
                break
            response = data.decode('utf-8')
            response_queue.put(response)


def handle_user_input(sock):
    while True:
        # Check if there's input ready to be read from sys.stdin
        if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
            # Handle user input
            user_input = input("Enter your message or type 'QUIT' to exit: ")
            if user_input.upper() == "QUIT":
                send_request(sock, "QUIT")
                break
            send_request(sock, user_input)


def main():
    if len(sys.argv) != 3:
        print("Usage: python client.py <hostname> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))

            response_queue = Queue()

            # Issue JOIN request
            join_command = input("Enter 'JOIN' followed by your username: ")
            if join_command.upper().startswith("JOIN "):
                send_request(s, join_command)
                response = response_queue.get()
                print(response)

                if response != "Username already taken. Please choose another.":
                    username = join_command.split()[1]

                    # Receive response thread to constantly scan for msg/broadcast
                    receive_thread = threading.Thread(target=receive_response, args=(s, response_queue))
                    receive_thread.daemon = True
                    receive_thread.start()

                    # Input thread to constantly handle user input
                    input_thread = threading.Thread(target=handle_user_input, args=(s,))
                    input_thread.daemon = True
                    input_thread.start()

                    # Main loop for handling input and responses
                    while True:
                        pass

            else:
                print("Invalid command. Please enter 'JOIN' followed by your username (JOIN {username})")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()