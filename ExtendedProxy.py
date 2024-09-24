#Importing packages
import socket
import ssl
import threading
from urllib.parse import urlparse
import time

def extract_host(request):
    # Extract the Host header from the HTTP request
    # Extract host and port number from http request
    for line in request.split(b'\n'):
        if line.startswith(b'Host:'):
            host_line = line.split(b' ')[1].strip()
            host_parts = host_line.split(b':')

            if len(host_parts) == 2:
                host, port = host_parts
                return host, int(port)
            else:
                # using 80 as a default port if not specified
                host = host_parts[0]
                return host, 80

    return None, None

def handle_client(client_sock):

    try:
        #receiving Client request
        request = client_sock.recv(4096)

        if request:

            target_host, target_port = extract_host(request)
            print(f"Target Host = {target_host}")

            if target_host:
                # Create a socket
                server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Connect to Target Host and Target Port
                server_sock.connect((target_host, target_port))

                if target_port == 443:  # HTTPS
                    # Wrap the server socket in an SSL/TLS connection
                    server_sock = ssl.wrap_socket(server_sock, server_side=False)

                # Send the request to the target server
                server_sock.send(request)

                # Receive the server's response
                while True:
                    server_response = server_sock.recv(4096)

                    if len(server_response) == 0:  # No response
                        break

                    # Check if this is the base HTML response
                    if b'Content-Type: text/html' in server_response:
                        # Parse HTML for objects and fetch them
                        server_response = parse_and_fetch_objects(server_response, target_host, target_port)

                    client_sock.send(server_response)


    #handeling Exceptions
    except ConnectionResetError as con_e:
        print(f"Client connection reset: {con_e}\n")

    except socket.error as soc_e:
        print(f"Socket error: {soc_e}\n")

    except Exception as exc_e:
        print(f"An error occurred: {exc_e}\n")

    finally:

        client_sock.close()
        server_sock.close()

#Parsing and fetching objects from html response
def parse_and_fetch_objects(html_response, target_host, target_port):

    # Parse the HTML response to find object URLs and fetch them
    html_response = html_response.decode('utf-8', errors='ignore')
    lines = html_response.split('\n')
    new_html = []
    object_urls = set()

    for line in lines:
        if line.strip().startswith('<script') or line.strip().startswith('<img') or line.strip().startswith('<link'):
            url = get_object_url(line)
            if url:
                object_urls.add(url)

    # Fetch objects in parallel using threading
    object_responses = fetch_objects_in_parallel(object_urls, target_host, target_port)

    # Replace object URLs in the HTML with the fetched content
    for line in lines:
        if line.strip().startswith('<script') or line.strip().startswith('<img') or line.strip().startswith('<link'):
            url = get_object_url(line)
            if url in object_responses:
                new_html.append(object_responses[url].decode('utf-8', errors='ignore'))
            else:
                new_html.append(line)
        else:
            new_html.append(line)

    return '\n'.join(new_html).encode('utf-8')

#Getting object URLs
def get_object_url(line):
    # getting url of objects
    parts = line.split('src=')
    if len(parts) > 1:
        url = parts[1].split()[0].strip('\'"')
        return url
    return None


#Parallel Object Fetching (Parallel Connection)
def fetch_objects_in_parallel(object_urls, target_host, target_port):

    #fetching objects Parallelly
    object_responses = {}
    threads = []

    for url in object_urls:
        t = threading.Thread(target=fetch_object, args=(url, target_host, target_port, object_responses))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return object_responses


#Fetching Object
def fetch_object(url, target_host, target_port, object_responses):

    # Fetch an object from the target server
    try:
        #created socket for fetching objects
        object_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        parsed_url = urlparse(url)
        object_socket.connect((target_host, target_port))

        if parsed_url.scheme == 'https':
            object_socket = ssl.wrap_socket(object_socket, server_side=False)

        object_request = f"GET {parsed_url.path} HTTP/1.1\r\nHost: {target_host}\r\n\r\n".encode('utf-8')
        object_socket.send(object_request)

        response = b""
        while True:
            chunk = object_socket.recv(4096)
            if not chunk:
                break
            response += chunk

        object_responses[url] = response
        object_socket.close()

    except Exception as e:
        print(f"Failed to fetch object {url}: {e}")
#assignning Host and port number to the speedy proxy
proxy_host = '127.0.0.1'
proxy_port = 9696

#Created Sockets for Communication
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((proxy_host, proxy_port))
server.listen(5)

print(f"Proxy server listening on {proxy_host}:{proxy_port}")

flag = 0
i = 0

while True:

    #Accepting Client requests
    client_sock, address = server.accept()
    i = i+1
    if (flag == 0):
        #store Start time
        start_time = time.time()
        flag = 1

    print(f"Accepted connection from {address[0]}:{address[1]}")
    multiple_clients = threading.Thread(target=handle_client, args=(client_sock,))
    multiple_clients.start()

    #store End time
    end_time = time.time()

    #Calculate Total time required
    total_time = (end_time - start_time)*1000
    print(f"Total time till object{i}: {total_time} msec\n")

