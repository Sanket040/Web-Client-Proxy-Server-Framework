#Importing Packages
import socket
import threading
import os

#Handling Client using Threads
def handle_client(client_sock):

    #receiving client Request form proxy server or client directly
    request = client_sock.recv(1024)

    #Spliting the request
    request_lines = request.split(b'\r\n')
    print(f"Request Line : {request_lines}\n")

    # Parse the HTTP request to get the requested file
    if len(request_lines) > 0:

        request_line = request_lines[0].decode()

        parts = request_line.split()
        print(f"Parts : {parts}\n")

        if len(parts) >= 2:
            #Removing '/'
            file_path = os.path.join('',parts[1][1:])
            print(f"File Path : {file_path}\n")

        else:
            #if no file is given it set default to index.html
            file_path = os.path.join('', 'index.html')
            print(f"File Path : {file_path}\n")

        try:
            #Reading Binary
            with open(file_path, 'rb') as file:
                content = file.read()

                # Status : 200 OK
                response = b'HTTP/1.1 200 OK\r\n\r\n' + content

        except FileNotFoundError:

            # Status : 404 Not Found
            response = b'HTTP/1.1 404 Not Found\r\n\r\nFile Not Found'

        client_sock.send(response)
        client_sock.close()

#Set Host and port numbers
server_host = '127.0.0.1'
server_port = 9698

#Create socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((server_host, server_port))
server.listen(5)

print(f"Server is listening on {server_host}:{server_port}")

while True:
    #Accept New client connection
    client_sock, address = server.accept()
    print(f"Accepted connection from {address[0]}:{address[1]}")

    #Creating thread
    multiple_clients = threading.Thread(target=handle_client, args=(client_sock,))
    multiple_clients.start()
                                                                                  