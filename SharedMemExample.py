import struct
import time

import numpy as np
from multiprocessing.sharedctypes import RawArray
from multiprocessing import Process


class Memory:
    sharedMemBlock = None
    size = 0
    memblock = None

    def __init__(self, size=-1, create=True):
        self.sharedMemBlock = RawArray("c", size)
        self.size = size
        self.memblock = np.ndarray((size,), dtype='<u1', buffer=self.sharedMemBlock)  # 8bitlik liste
        if (create):
            self.memblock[:] = 48  # 0'ın ascii değeri stringler diğer türlü sıkıntı çıkarabiliyor

    def __getitem__(self, item):
        return self.memblock[item]

    def __setitem__(self, key, value):
        self.memblock[key] = value


class DataPacket(Memory):
    # burda önemli olan sharedMemBlock bunun processlere dağıtılması gerekiyor
    def __init__(self, datpacket=None):
        if datpacket is None:
            super().__init__(120)  # 120 bytelık bir memory oluştur
            self.isOkey = False  # bool (iyi değilmiş :c umarım yakın zamanda iyi olur)
            self.positionX = 0  # int
            self.positionY = 0  # float
            self.positionZ = 0  # unsigned int
            self.yaw = 0  # double
            self.mode = ""  # string (büyüklüğü unutmayın sonra memory corruption olur)
            # yada hata verir denemedim :P


        else:  # data paketini aktarmak için sharedmemblock (yani shared memory objesi) ni aktarman lazım diğer türlü
            # bağlantıları kopuyor
            self.sharedMemBlock = datpacket.sharedMemBlock
            self.size = datpacket.size
            self.memblock = np.ndarray((self.size,), dtype='<u1', buffer=self.sharedMemBlock)

    # datalara ulaşmak için property kullanıcaz
    # data okurken memblockdan
    # data yazarken sharedMemBlocka yazıcaz çünkü sharedMemBlock processler arası paylaşılan bir memory
    # ama memblock processe özel yukarıdaki buffera verilen değer bir pointer gibi işliyor
    # bool 1 bit
    @property
    def isOkey(self):
        return self.memblock[0]

    @isOkey.setter
    def isOkey(self, value):
        self.sharedMemBlock[0] = value > 0

    # int 4 byte
    @property
    def positionX(self):
        return struct.unpack('i', self.memblock[1:5])[0]

    @positionX.setter
    def positionX(self, value):
        self.sharedMemBlock[1:5] = struct.pack('i', value)

    # float 4 byte
    @property
    def positionY(self):
        return struct.unpack('f', self.memblock[5:9])[0]

    @positionY.setter
    def positionY(self, value):
        self.sharedMemBlock[5:9] = struct.pack('f', value)

    # unsigned int 4 byte
    @property
    def positionZ(self):
        return struct.unpack('I', self.memblock[9:13])[0]

    @positionZ.setter
    def positionZ(self, value):
        self.sharedMemBlock[9:13] = struct.pack('I', value)

    # double 8 byte
    @property
    def yaw(self):
        return struct.unpack('d', self.memblock[13:21])[0]

    @yaw.setter
    def yaw(self, value):
        self.sharedMemBlock[13:21] = struct.pack('d', value)

    # 10 karakterlik string 10 byte

    @property
    def mode(self):
        mes = self.memblock[21:31].tobytes().decode('utf-8')
        return mes[:mes.find('\0')]

    @mode.setter
    def mode(self, value):
        if (len(value) > 10):  # buraya maksimum 10 karakter yazılabilir
            value = value[:10]

        # ayrıca 10 ten aşşağı karakter de yazılamaz bu yüzden
        # böyle bir güvenlik konulmalı
        # elif (len(value) < 10):
        #    value += '\0 ' * (10 - len(value))
        # self.sharedMemBlock[21:31] = value.encode('utf-8')

        # ama diyelim ki 50 karakterin var ve 50den aşşağı karakter
        # yazmak istiyorsan bu şekilde yapabilirsin bizim qr datası
        # tarafı böyle
        if ((value == "") or (value is None) or (value == "\0") or (value == '')):
            value = "\0" * 10  # bunun 50 olduğunu varsay
        val = np.frombuffer((value + "\0").encode("utf-8"), dtype=np.int8)

        valLen = len(val)
        self.memblock[21:(21 + valLen)] = val

    # tüm bu propertyleri yaptıktan sonra bunlara initte default değer atamalısın
    # çünkü default değerleri şu anda çok saçma durumda listenin tamamında 49 yazıyor


def process1(sharedMem):
    myPacket = DataPacket(sharedMem)
    while 1:
        myPacket.isOkey = not myPacket.isOkey
        myPacket.positionX += 1
        myPacket.positionY += 0.1
        myPacket.positionZ += 1
        myPacket.yaw += 0.001
        print("\nmode: " + myPacket.mode + "\n")
        time.sleep(0.5)


if __name__ == "__main__":
    packet = DataPacket()  # ilk önce Memoryi oluşturuyoruz

    # print(packet.isOkey)
    # packet.isOkey = True
    # print(packet.isOkey)
    # packet.mode = "iyimit"
    # print(packet.mode)
    # packet.mode = "ikt"
    # print(packet.mode)

    p1 = Process(target=process1, args=(packet,))  # data paketini aktarmak için sharedmemblock (yani shared memory
    # objesi) ni aktarman lazım diğer türlü bağlantıları kopuyor

    p1.start()

    den = 1
    while 1:
        print("isOkey: " + str(packet.isOkey))
        print("positionX: " + str(packet.positionX) + " positionY: " + str(packet.positionY) + " positionZ: " + str(
            packet.positionZ))
        print("yaw: " + str(packet.yaw))
        packet.mode = "O-O)" + str(den)
        den += 1
        time.sleep(0.3)
