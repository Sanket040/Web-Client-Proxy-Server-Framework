#importing packages
import socket
import ssl
import threading
import time

def extract_host(request):
    # Extracting the Header

    #spliting the Request to get host and port from request
    for line in request.split(b'\n'):
        if line.startswith(b'Host:'):
            host_line = line.split(b' ')[1].strip()
            host_parts = host_line.split(b':')

            if len(host_parts) == 2:
                host, port = host_parts
                return host, int(port)
            else:
                #if Request doesnt contain port then default port set to 80
                host = host_parts[0]
                return host, 80

    return None, None

#Each thread thread will be handeled here
def handle_client(client_sock):

    try:

        #receiving Client request
        request = client_sock.recv(4096)

        #calling function to extract request coming from the client
        if request:
            target_host,target_port = extract_host(request)
            print(f"Target Host = {target_host}")

            if target_host:

                #Create Socket
                server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Connecting to the server host and server port
                server_sock.connect((target_host, target_port))

                if target_port == 443:

                    # Wraping up server socket in an SSL connection
                    server_sock = ssl.wrap_socket(server_sock, server_side=False)

                #sending request to the web server
                server_sock.send(request)

                #Receiving the web server responce
                while True:

                    server_response = server_sock.recv(4096)

                    if len(server_response) == 0:
                        break
                    #Sending Responce to the client
                    client_sock.send(server_response)

    #Handling Exception
    except ConnectionResetError as connection:
        print(f"Client connection reset: {connection}\n")

    except socket.error as soc_error:
        print(f"Socket error: {soc_error}\n")

    except Exception as exc_error:
        print(f"An error occurred: {exc_error}\n")

    finally:
        #Closing Connection
        client_sock.close()
        server_sock.close()


#Assigning Host and port to Proxy
proxy_host = '127.0.0.1'
proxy_port = 9697

#creating Socket for comminucating with server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#binding Socket with proxy host and port
server.bind((proxy_host, proxy_port))
server.listen(5)

print(f"Proxy server listening on {proxy_host}:{proxy_port}")

flag = 0
i = 0

while True:
    #Accepting requests
    client_sock, address = server.accept()

    #Store Starting time
    i = i+1
    if (flag == 0):
        start_time = time.time()
        flag = 1

    print(f"Accepted connection from {address[0]}:{address[1]}")

    #Create thread to handle multiple clients
    multiple_clients = threading.Thread(target=handle_client, args=(client_sock,))
    multiple_clients.start()

                                                                          
                                                                   