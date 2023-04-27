import os
import math
import json
import datetime
import numpy as np
from geopy.distance import geodesic, distance


def MapValue(value: float, inmin, inmax, outmin, outmax, force=True):
    a = (value - inmin) * (outmax - outmin) / (inmax - inmin) + outmin
    if (force):
        if outmax > outmin:
            if a > outmax:
                a = outmax
            elif a < outmin:
                a = outmin
        else:
            if a < outmax:
                a = outmax
            elif a > outmin:
                a = outmin
    return a


class Distance:
    @staticmethod
    def GetGeoDistance2D(point1, point2):
        return geodesic(point1, point2).meters

    @staticmethod
    def GetGeoDistance3D(point1, point2):
        dist = geodesic([point1[0], point1[1]], [point2[1][0], point2[1][1]]).meters
        return np.sqrt(dist ** 2 + np.power(point1[2] - point2[1][2], 2))

    @staticmethod
    def GetDistance1D(x, y):
        return np.abs(x - y)

    @staticmethod
    def GetDistance2D(x1, y1, x2, y2):
        return np.sqrt(np.power(x1 - x2, 2) + np.power(y1 - y2, 2))

    @staticmethod
    def GetDistance3D(Point1: list, Point2: list):
        return np.sqrt(
            np.power(Point1[0] - Point2[0], 2) + np.power(Point1[1] - Point2[1], 2) + np.power(Point1[2] - Point2[2],
                                                                                               2))

    @staticmethod
    def hypotenuse(a, b):
        return np.sqrt(np.power(a, 2) + np.power(b, 2))

    @staticmethod
    def DistanceCenter(x, y, height, width):
        cx = x - width / 2
        cy = -(y - height / 2)
        dis = np.sqrt(np.power(x - width / 2, 2) + np.power(y - height / 2, 2))

        return cx, cy, dis

    @staticmethod
    def coordinateToMeter(self, refPoint: list, point: list, addCord=False):
        posx = geodesic(refPoint, [refPoint[0], point[1]]).m
        posy = geodesic(refPoint, [point[0], refPoint[1]]).m
        if (refPoint[0] - point[0]) > 0:
            posy = -posy
        if (refPoint[1] - point[1]) > 0:
            posx = -posx
        if addCord:
            return [[posx, posy], [point[0], point[1]]]
        return [posx, posy]

    @staticmethod
    def meterToCoordinate(refPoint: list[float], point: list[float]):
        posx, posy = point[0], point[1]

        if posx > 0:
            posx = distance(kilometers=posx / 1000).destination(refPoint, 90)
        else:
            posx = -posx
            posx = distance(kilometers=posx / 1000).destination(refPoint, -90)

        if posy > 0:
            posy = distance(kilometers=posy / 1000).destination(refPoint, 0)
        else:
            posy = -posy
            posy = distance(kilometers=posy / 1000).destination(refPoint, 180)

        return [float('{0:.8f}'.format(posy.latitude)), float('{0:.8f}'.format(posx.longitude))]

class Angle:
    @staticmethod
    def angleCheck(x1, y1, x2, y2):
        sign = Angle.signCheck(x1, y1, x2, y2)
        if sign % 2 == 0:
            a = np.rad2deg(math.atan2(y1 - y2, x1 - x2))
        else:
            a = np.rad2deg(math.atan2(y2 - y1, x2 - x1))
        return float("{:.4f}".format(a)), sign

    @staticmethod
    def signCheck(x1, y1, x2, y2):
        # ilk nokta orijin
        if (x2 - x1 > 0) & (y2 - y1 > 0):
            return 1  # 1.bölge

        elif (x2 - x1 < 0) & (y2 - y1 > 0):
            return 2  # 2.bölge

        elif (x2 - x1 < 0) & (y2 - y1 < 0):
            return 3  # 3.bölge

        else:
            return 4  # 4.bölge


class JsonFuncs:
    @staticmethod
    def JsonWrite(Data, FileName, FileLocation):
        with open(FileLocation + FileName, "w") as write_file:  # json dosyası oluştur/sıfırla
            json.dump(Data, write_file)  # datayı json iiçine yaz

    @staticmethod
    def ReadJson(FileName):
        with open(FileName) as json_file:  # json dosyasını aç
            return json.load(json_file)  # verileri oku


class FileFuncs:
    @staticmethod
    def Write(Data, FileName, mode="w"):
        with open(FileName, mode) as write_file:  # json dosyası oluştur/sıfırla
            write_file.write(Data)  # datayı json iiçine yaz

    @staticmethod
    def Add(Data, FileName, mode="a"):
        with open(FileName, mode) as add_to_file:
            add_to_file.write(Data)
            add_to_file.close()

    @staticmethod
    def Read(FileName):
        with open(FileName) as file:  # json dosyasını aç
            return file.readlines()  # verileri oku

    @staticmethod
    def GetFiles(fileloc: str, fileType: str):
        files = [os.listdir(fileloc)]
        FilesList = []
        for temp in files:
            if len(temp) != 0:

                for g in range(len(temp)):
                    if temp[g].endswith(fileType):
                        FilesList.append(temp[g])
                        pass
        return FilesList


def GetTimestamp(forName):
    if (forName):
        return datetime.datetime.now().strftime('%m-%d_%H-%M-%S-%f')[:-3]
    else:
        return datetime.datetime.now().strftime('%H:%M:%S:%f')[:-3]
