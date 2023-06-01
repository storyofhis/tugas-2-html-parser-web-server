import os
import socket
import select
import sys


BASE_DIR = os.path.dirname(os.path.realpath(__file__))

class HTTPServer:
    def __init__(self, host, port):
        self.server_socket = None
        self.host = host
        self.port = port

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Step 1: Create a socket
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Step 2: Set socket options
        self.server_socket.bind((self.host, self.port))  # Step 3: Bind socket to the host and port
        self.server_socket.listen(5)  # Step 4: Start listening for connections

        input_socket = [self.server_socket]  # Step 5: Add the server socket to the input sockets list

        try:
            while True:
                read_ready, write_ready, exception = select.select(input_socket, [], [])  # Step 6: Wait for input

                for sock in read_ready:
                    if sock == self.server_socket:
                        client_socket, client_address = sock.accept()   # Step 7: Accept incoming connection
                        input_socket.append(client_socket)  

                    else:
                        data = sock.recv(4096)
                        data = data.decode('utf-8')
                        request_header = data.split('\r\n')
                        if not data:
                            sock.close()
                            input_socket.remove(sock)
                            continue
                        
                        request_file = data.splitlines()[0].split()[1]
                        response_header = b''
                        response_data = b''
                        
                        # Step 8: Handle received data
                        # ATTENTION: PLEASE DO NOT CHANGE CODE BELOW THIS LINE
                        if '/exit' in data:
                            sock.sendall(b'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n')
                            return
                        # ATTENTION: PLEASE DO NOT CHANGE CODE ABOVE THIS LINE


                        # this is a special case, where the server should return the index.html file
                        if request_file == '/' or request_file == '/index' or request_file == '/index.html':
                            f = open(os.path.join(BASE_DIR, 'index.html'), 'r')
                            response_data = f.read()
                            f.close()

                            content_length = len(response_data)
                            response_header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' \
                                            + str(content_length) + '\r\n\r\n'

                            # send response header and data
                            sock.sendall(response_header.encode('utf-8') + response_data.encode('utf-8'))

                        else:
                            # check request file
                            file_path = os.path.join(BASE_DIR, request_file.replace('/','',1))
                            if os.path.isdir(file_path):
                                # Show directory contents
                                dir_contents = os.listdir(file_path)
                                response_data = ''
                                for i in dir_contents:
                                    response_data += '<li><a href="">' + i +'</li>'
                                response_header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' \
                                            + str(len(response_data)) + '\r\n\r\n'
                                sock.sendall(response_header.encode() + response_data.encode())

                            elif os.path.exists(file_path):
                                if file_path.endswith('.html'):
                                    # Read html file and send to client
                                    with open(file_path, 'r') as f:
                                        response_data = f.read()
                                    content_length = len(response_data)
                                    response_header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' \
                                            + str(content_length) + '\r\n\r\n'
                                    sock.sendall(response_header.encode('utf-8') + response_data.encode('utf-8'))

                                else:
                                    # Read other file types and send to client as download
                                    with open(file_path, 'rb') as f:
                                        response_data = f.read()
                                    content_length = len(response_data)
                                    response_header = 'HTTP/1.1 200 OK' + '\r\nContent-Disposition:attachment;filename=\"' + request_file.split('/')[2] +'\"\r\nContent-Length:' \
                    + str(content_length) + '\r\n\r\n'
                                    sock.sendall(response_header.encode() + response_data)

                            else:
                                # Return 404
                                f = open(os.path.join(BASE_DIR, '404.html'), 'r')
                                response_data = f.read()
                                f.close()

                                content_length = len(response_data)
                                response_header = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' \
                                    + str(content_length) + '\r\n\r\n'

                                # send response header and data
                                sock.sendall(response_header.encode() + response_data.encode())

        except KeyboardInterrupt:
            self.server_socket.close()
            sys.exit(0)

    def stop(self):
        print("Shutting down server...")
        self.server_socket.close()
        sys.exit(0)

if __name__ == '__main__':
    # TODO: Parse and set the host and port from the config file
    port, host = open(os.path.join(BASE_DIR, 'httpserver.conf'), 'r').read().replace('PORT=', '').replace('HOST=','').split('\n')
    server = HTTPServer(host, int(port))
    server.start()
    server.stop()