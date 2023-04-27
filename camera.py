import cv2
import numpy as np

from time import sleep


class CameraObject():
    capture = None
    isCamOpened = False
    ScreenCapture = False
    Receive = False
    recv = None
    mon = {'left': 1026, 'top': 518, 'width': 890, 'height': 500}

    def initialize(self, Path, WaitReady=False, ScreenCapture=False, Receive=False):
        if Receive:
            self.Receive = True
            import VideoReceiverUdp
            if (Path is not None):
                self.recv = VideoReceiverUdp(Path[0], Path[1])
            else:
                self.recv = VideoReceiverUdp()
            pass
        else:
            if ScreenCapture:
                from mss import mss
                self.ScreenCapture = True
                self.sct = mss()
                pass
            else:

                self.capture = cv2.VideoCapture(Path)
                while not self.capture.isOpened() and WaitReady:
                    sleep(0.1)
                    print("kamera acılamıyor")
        self.isCamOpened = True

    def __init__(self, Path=0, WaitReady=False, ScreenCapture=False, Receive=False, intialize=True):
        if (intialize):
            self.initialize(Path, WaitReady, ScreenCapture, Receive)

    def release(self):
        if self.ScreenCapture:
            pass
        else:
            if self.Receive:
                self.recv.serv.socket.close()
            else:
                self.capture.release()
        self.isCamOpened = False

    def Read(self, mon=None):

        if (self.recv):
            return self.recv.Read()
        if (self.ScreenCapture):
            if mon is not None:
                frame = np.array(self.sct.grab(mon))
            else:
                frame = np.array(self.sct.grab(self.mon))
            frame = frame[:, :, ::-1]
            frame = frame[:, :, 1::]
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            ret, frame = self.capture.read()

            return frame
