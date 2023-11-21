import socket
import sys

def send_message(sock, message):
    sock.send(message.encode('utf-8'))

def receive_message(sock):
    return sock.recv(1024).decode('utf-8')

def join_server(sock, username):
    send_message(sock, f"JOIN {username}")
    response = receive_message(sock)
    print(response)

def list_users(sock):
    send_message(sock, "LIST")
    response = receive_message(sock)
    print(response)

def send_direct_message(sock, to_user, message):
    send_message(sock, f"MESG {to_user} {message}")
    response = receive_message(sock)
    print(response)

def send_broadcast_message(sock, message):
    send_message(sock, f"BCST {message}")
    response = receive_message(sock)
    print(response)

def quit_server(sock):
    send_message(sock, "QUIT")
    response = receive_message(sock)
    print(response)
    sock.close()

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 client.py <hostname> <port>")
        sys.exit(1)

    hostname = sys.argv[1]
    port = int(sys.argv[2])

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #try:
    client_socket.connect((hostname, port))
    #except Exception as e:
     #   print(f"Error connecting to the server: {e}")
      #  sys.exit(1)

    print("Connected to the server.")

    username = input("Enter your username: ")
    join_server(client_socket, username)

    while True:
        print("\nOptions:")
        print("1. List Users")
        print("2. Send Direct Message")
        print("3. Send Broadcast Message")
        print("4. Quit")

        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            list_users(client_socket)
        elif choice == "2":
            to_user = input("Enter the username of the recipient: ")
            message = input("Enter your message: ")
            send_direct_message(client_socket, to_user, message)
        elif choice == "3":
            message = input("Enter your broadcast message: ")
            send_broadcast_message(client_socket, message)
        elif choice == "4":
            quit_server(client_socket)
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
