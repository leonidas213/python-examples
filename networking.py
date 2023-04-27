import zlib
import socket
import os
import struct


class Networking:

    @staticmethod
    def SendMessageTCP(Data="", IP='', Port=0, compress=False, receive=False, PacketSize=65536, timeout=0.8):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # soketi oluştur ve client olarak ata
        if (timeout > 0):
            client.settimeout(timeout)
        client.connect((IP, Port))  # soketi bağla

        if compress:

            client.sendall(zlib.compress(Data.encode("utf-8")))  # mesajı sıkıştır gönder
        else:
            client.sendall(Data.encode("utf-8"))  # mesajı sıkıştırmadan gönder
            # mesaj var ise al
        if receive:
            a = client.recv(PacketSize)
            return a.decode("utf-8")
        return

    @staticmethod
    def SendMessageUDP(Data="", IP='', Port=0, compress=False, receive=False):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # soketi oluştur ve client olarak ata
        if compress:
            client.sendto(zlib.compress(Data.encode("utf-8")), (IP, Port))  # mesajı sıkıştır gönder
        else:
            client.sendto(Data.encode("utf-8"), (IP, Port))  # mesajı sıkıştırmadan gönder
        if receive:
            a = client.recvfrom(65536)  # mesaj var ise al
            mess, addr = a
            return mess.decode("utf-8"), addr
        return ""

class ServerTCP:
    def __init__(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((ip, port))

    def Listen(self):  # serverı dinlemeye al
        self.socket.listen()
        conn, addr = self.socket.accept()
        return conn, addr

    def ListenReceive(self, length=65536, compress=False):  # serverı dinlemeye al
        self.socket.listen()
        conn, addr = self.socket.accept()
        return self.ReceiveMessage(conn, length, compress)

    @staticmethod
    def ReceiveMessage(conn, length=65536, compress=False):  # mesajı al
        if compress:
            return zlib.decompress(conn.recv(length)).decode("utf-8")
        else:
            return conn.recv(length).decode("utf-8")

    @staticmethod
    def SendMessage(message: str, conn):  # mesaj gönder
        conn.send(message.encode("utf-8"))

class ServerUDP:

    def __init__(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip, port))

    def __del__(self):
        self.socket.close()

    def ListenRecv(self, decode=True, decompress=False):  # serverı dinlemeye al ve mesaj al
        packet = self.socket.recvfrom(65536)
        if decode:
            if decompress:
                msg = zlib.decompress(packet[0]).decode("utf-8")
            else:
                msg = packet[0].decode("utf-8")

        else:
            if decompress:
                msg = zlib.decompress(packet[0])
            else:
                msg = packet[0]
        addr = packet[1]
        return msg, addr

    def SendMessage(self, message: str, addr):  # mesaj gönder
        self.socket.sendto(message.encode("utf-8"), addr)

class Pipeline:

    def __init__(self, PipeName: str, Create=False):
        if Create:
            os.mkfifo(r'\\.\pipe/' + PipeName)
        self.PipeName = PipeName
        self.f = open(r'\\.\pipe/' + PipeName, 'r+b', 0)

    def Close(self):
        os.unlink(r'\\.\pipe/' + self.PipeName)

    def WriteRead(self, msg: str, CompressWrite=False, CompressRead=False):
        self.Write(msg, CompressWrite)
        return self.Read(CompressRead)

    def Write(self, msg: str, compress=False):
        if compress:
            msg = zlib.compress(msg.encode("utf-8"))
        else:
            msg = msg.encode("utf-8")
        self.f.write(struct.pack('I', len(msg)) + msg)  # Write str length and str
        self.f.seek(0)  # EDIT: This is also necessary

    def Read(self, compress=False) -> str:
        Packet = struct.unpack('I', self.f.read(4))[0]  # Read str length
        incomingMessage = self.f.read(Packet)
        self.f.seek(0)  # Important!!!
        if compress:
            incomingMessage = zlib.decompress(incomingMessage)
        else:
            incomingMessage = incomingMessage.decode('ascii')  # Read str
        return incomingMessage

