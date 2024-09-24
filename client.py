#importing packages
import socket
from bs4 import BeautifulSoup

#Taking a choice from client that it wants connection through Proxy Server or Direct server
choice = input("Press P if you want connection through proxy Server else press S : ")


if choice == 'P':
    #Enter Proxy host, port, Server host, port and path
    proxy_host = input("Enter Proxy Host : ")
    proxy_port = int(input("Enter Proxy Port : "))
    server_host = input("Enter host name : ")
    server_port = int(input("Enter port number :"))
    path = input("Enter path : ")

    #Create an Object for Socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Making a Conection with the Proxy Server
    client_socket.connect((proxy_host, proxy_port))

    #Generating A GET request
    request = f"GET {path} HTTP/1.1\r\nHost: {server_host}:{server_port}\r\n\r\n"

    #Send Request to the Web Proxy
    client_socket.send(request.encode())

    #receiving responce
    response = b''
    while True:
        data = client_socket.recv(4096)
        if not data:
            break
        response += data
    #Print Received Responce
    print(response.decode())

    #Closing Connection with proxy
    client_socket.close()

    #Using Beautifulsoup for Parsing objects
    soup = BeautifulSoup(response.decode(), 'html.parser')
    paths = []
    for atag in soup.find_all('a'):
        paths.append(atag['href'])
    #Filtering out HTML files from the parsed objects
    html_paths = [path for path in paths if path.startswith('/') and path.endswith('.html')]

    #for Fetching Objects One by one using Non-Persistent Connection
    i=0
    for obj_path in html_paths :
        #initialized object host and port
        obj_host = server_host
        obj_port = server_port

        #Created connection for each object
        obj_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        obj_socket.connect((proxy_host, proxy_port))

        #creating request for proxy Server
        request = f"GET {obj_path} HTTP/1.1\r\nHost: {obj_host}:{obj_port}\r\n\r\n"

        #Sending Request to proxy server
        obj_socket.send(request.encode())

        #Receiving Responce from Proxy server
        obj_response = b''
        while True:
            obj_data = obj_socket.recv(4096)
            if not obj_data:
                break
            obj_response += obj_data
        print(obj_response.decode())
        i+=1
        print("..............................Received Obj - ",i,"..................................")

        #Closig Object socket
        obj_socket.close()


#If client wants Responce directly from the server
else :

    #Getting Server host, port and path
    server_host = input("Enter host name : ")
    server_port = int(input("Enter port number :"))
    path = input("Enter path : ")

    #creating Client Socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Connecting to the server
    client_socket.connect((server_host, server_port))

    #Creating Request
    request = f"GET {path} HTTP/1.1\r\nHost: {server_host}:{server_port}\r\n\r\n"

    #Sending Request to the web server
    client_socket.send(request.encode())

    #receiving Request From the Server
    response = b''
    while True:
        data = client_socket.recv(4096)
        if not data:
            break
        response += data
    #Pring Responce
    print(response.decode())

    #Closing Client Connection
    client_socket.close()


    #Using Beautifulsoup for Parsing objects
    soup = BeautifulSoup(response.decode(), 'html.parser')
    paths = []
    for atag in soup.find_all('a'):
        paths.append(atag['href'])

    #Filtering out HTML files from the parsed objects
    html_paths = [path for path in paths if path.startswith('/') and path.endswith('.html')]


    #for Fetching Objects One by one using Non-Persistent Connection
    i=0
    for obj_path in html_paths :

        #initialized object host and port
        obj_host = server_host
        obj_port = server_port

        #Creating Object for socket
        obj_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #Connecting to the web server
        obj_socket.connect((obj_host, obj_port))

        #Creating and Sending Get request to the Web server
        request = f"GET {obj_path} HTTP/1.1\r\nHost: {obj_host}:{obj_port}\r\n\r\n"
        obj_socket.send(request.encode())

        #Receiving Responces coming from the web server
        obj_response = b''
        while True:
            obj_data = obj_socket.recv(4096)
            if not obj_data:
                break
            obj_response += obj_data

        #Printing responces coming from the web server
        print(obj_response.decode())
        i+=1
        print("..............................Received Obj",i,"..................................")
        obj_socket.close()
