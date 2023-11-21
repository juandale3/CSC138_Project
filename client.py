import socket
import sys
import threading

def receive_messages(sock): # Function to receive messages
    while True:
        try:
            data = sock.recv(1024).decode('utf-8')
            #if not data:
             #   break
            print(data)
        except socket.error as e:
            print(f"Error receiving message: {e}")
            break

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 client.py <hostname> <port>")
        sys.exit(1)

    hostname = sys.argv[1]
    port = int(sys.argv[2])

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP Connection to connect to appr. server
    client_socket.connect((hostname, port))
    print("Connected to the server.")
    #JOIN request
    try:
        while True:
            
            username = input("Please enter JOIN folowed by your username: ") # JOIN command to set username
            if username.upper().startswith("JOIN "):
                client_socket.send(username.encode('utf-8'))
                dat = client_socket.recv(1024).decode('utf-8')
                print(dat)
                break
            else:
                print("invalid response please enter again")
        rec_thread = threading.Thread(target=receive_messages, args=(client_socket,)) # thread to constantly scan
        # for messages
        rec_thread.start()
        while True:
            #rec_thread.start()
            inp = input("Please enter a argument: ") # argument parser
            command, *args = inp.split()
            # print("here are the arguments")
            # print(command)
            # print(args) #ERROR CHECKING FOR INPUTS
            if command == "QUIT":
                client_socket.send(command.encode('utf-8'))
                break
    
            client_socket.send(inp.encode('utf-8'))

            #dat = client_socket.recv(1024).decode('utf-8')
            
            #print(dat)
    except Exception as e:
        print(f"Error in the main client loop: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()