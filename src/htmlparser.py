import os
import socket
import sys
import ssl
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

class HTMLParser:
    # TODO:
    # 1. Assign semua value yang diperlukan
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.response = None
        self.header = None
        self.content = None

    def connect(self):
        # 2. Connect socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        
    def SSL(self):
        # 3. Connect SSL
        self.socket = ssl.wrap_socket(self.socket)

    def separate_header(self):
        # 4. Pisahkan header dan content
        if isinstance(self.response, bytes):
            header_end = self.response.find(b'\r\n\r\n')
            self.header = self.response[:header_end].decode('utf-8')
            self.content = self.response[header_end + 4:]
        else:
            header_end = self.response.find('\r\n\r\n')
            self.header = self.response[:header_end]
            self.content = self.response[header_end + 4:]

    def send_message(self, message):
        # 5. Kirim message dan terima response
        self.socket.sendall(message.encode())
        self.response = self.socket.recv(4096)
        self.separate_header()
    
    def get_status_code(self):
        if self.header is None:
            return None
        if isinstance(self.header, bytes):
            self.header = self.header.decode('utf-8')
        status_code =  self.header.split(' ')[1]
    
        if(status_code == "200"):
            return self.header.split(' ')[1] + " " + self.header.split(' ')[2].split('\n')[0]
        elif(status_code == "404"):
            return self.header.split(' ')[1] + " " + self.header.split(' ')[2] + " " + self.header.split(' ')[3].split('\n')[0]
    
    def get_content_encoding(self):
        # 7. Ambil content encoding
        encoding = None
        for line in self.header.split(b'\r\n'):
            if line.startswith(b'Content-Encoding'):
                encoding = line.split(b': ')[1].decode('utf-8')
                break
        return encoding
    
    def get_http_version(self):
        if self.header is None:
            return None
        if isinstance(self.header, bytes):
            self.header = self.header.decode('utf-8')
        return self.header.split(' ')[0]
    
    def get_charset(self):
        if self.header is None:
            return ''

        charset = None
        if isinstance(self.header, bytes):
            header_str = self.header.decode('utf-8')
        else:
            header_str = self.header

        lines = header_str.split('\n')
        for line in lines:
            if line.startswith('Content-Type:'):
                content_type = line.split(': ')[1]
                charset_start = content_type.find('charset=')
                if charset_start != -1:
                    charset_start += 8  # length of 'charset='
                    charset = content_type[charset_start:]
                    break
        return charset

    def get_menu(self):
        res = []
        soup = BeautifulSoup(self.content, 'html.parser')
        menu_items = soup.find_all('a')
        for item in menu_items:
            res.append('\t' + item.get_text().strip())
        return res

    def disconnect(self):
        self.socket.close()


if __name__ == "__main__":
    client = HTMLParser("classroom.its.ac.id", 443)
    client.connect()
    client.SSL()

    client.send_message(f"GET / HTTP/1.1\r\nHost: {client.host}\r\n\r\n")
    print(client.get_status_code())
    print(client.get_content_encoding())
    print(client.get_http_version())
    print(client.get_charset())
    print(client.get_menu())