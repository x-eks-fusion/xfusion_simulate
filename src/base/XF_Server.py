import socket
import struct
from threading import Thread

from handlers.XF_MCUHandler import MCUHandler


class Server:
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 8000

    def __init__(self, ip=SERVER_IP, port=SERVER_PORT):
        self.device = {}

        self.server_ip = ip
        self.server_port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.server_ip, self.server_port))
        self.server_socket.listen(5)
        self.mcu_handler = MCUHandler(self)
        print(
            f"Server listening on {self.server_ip}:{self.server_port}..."
        )

    def accept(self):
        client_socket, client_address = self.server_socket.accept()
        print(f"Connection established with {client_address}")
        return client_socket, client_address

    def handle(self, client_socket, client_address):
        def recvAll(sock, length):
            """接收指定长度的完整数据"""
            data = b''
            while len(data) < length:
                more = sock.recv(length - len(data))
                if not more:
                    raise ConnectionError(
                        "Client disconnected before receiving complete data"
                    )
                data += more
            return data
        try:
            # 先接收TLV中的Type（4字节）和Length（8字节），共12字节
            header = client_socket.recv(12)
            if not header:
                print(f"Client {client_address} disconnected")
                return False
            # 使用 struct 解包 Type 和 Length
            msg_id, msg_length = struct.unpack('<IQ', header)
            value = recvAll(client_socket, msg_length)
            self.mcu_handler.handle(client_socket, msg_id, value)
            return True
        except ConnectionError:
            print(
                f"Client {client_address} disconnected unexpectedly")
            return False


class ServerThread(Thread):

    def __init__(self):
        super().__init__()
        self.server = Server()
        self.setDaemon(True)

    # 重写 run() 方法
    def run(self):
        while True:
            client_socket, client_address = self.server.accept()
            while self.server.handle(client_socket, client_address):
                pass
            client_socket.close()


if __name__ == "__main__":
    server_thread = ServerThread()
    server_thread.start()
