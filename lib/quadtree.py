# -*- coding: utf-8 -*-
import sys

class Area:
    def __init__(self,x1,y1,x2,y2,level):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.level = level
        self.points_ = []
        self.fixed = False

    def append(self, p):
        """ 領域にデータ点を追加 """
        self.points_.append(p)

    def points(self):
        """ 領域に属しているデータ点を返す """
        return self.points_

    def is_fixed(self):
        """ 分割が終わっているかどうか """
        return self.fixed

    def set_fixed(self):
        """ 分割が終わったフラグを立てる """
        self.fixed = True

    def cover(self, p):
        """ あるデータ点pがこの領域にカバーされるかどうか """
        if self.x1 < p[0] and self.y1 < p[1] and self.x2 >= p[0] and self.y2 >= p[1]:
            return True
        else:
            return False

def divide(area,level):
    division = []

    """ 分割後の各辺の長さ """
    xl = (area.x2 - area.x1)/2
    yl = (area.y2 - area.y1)/2

    """ 分割後の領域を生成 """
    for dx in [0,1]:
        for dy in [0,1]:
            sub_area = Area(area.x1+dx*xl, area.y1+dy*yl, area.x1+(1+dx)*xl, area.y1+(1+dy)*yl,level)
            division.append(sub_area)

    """ 分割前の領域に属すデータ点を分割後の領域にアサイン """
    for p in area.points():
        for sub_area in division:
            if sub_area.cover(p):
                sub_area.append(p)
                break

    return division


def quadtree(data, initial, maxpoints, maxdivision):
    areas = [initial]

    """ 引数で与えられたmaxdivision回だけ分割を繰り返す """
    for n in range(maxdivision):
        new_areas = []
        for i in range(len(areas)):
            if not areas[i].is_fixed():
                """ まだ分割が終わっていない領域に対して """
                if len(areas[i].points()) > maxpoints:
                    """ 領域に属すデータ点の数がmaxpoints個を超えていたら分割 """
                    division = divide(areas[i],n+1)
                    for d in division:
                        new_areas.append(d)
                else:
                    """ 領域に属すデータ点の数がmaxpoints個を超えていなかったらもう分割しない """
                    areas[i].set_fixed()
                    new_areas.append(areas[i])
            else:
                """ 分割が終わっていればそのまま """
                new_areas.append(areas[i])
        areas = new_areas

    return areas


def read_data(file_name):
    data = []
    for line in open(file_name, 'r'):
        p = tuple([float(v) for v in line.rstrip().split(' ')])
        data.append(p)
    return data

if __name__ == '__main__':
    x1 = float(sys.argv[1])
    y1 = float(sys.argv[2])
    x2 = float(sys.argv[3])
    y2 = float(sys.argv[4])
    maxpoints = int(sys.argv[5])
    maxdivision = int(sys.argv[6])
    data = read_data(sys.argv[7])

    """ 対象とする領域を生成 """
    initial = Area(x1,y1,x2,y2,0)
    for d in data:
        initial.append(d)

    """ 分割 """
    qtree = quadtree(data, initial, maxpoints, maxdivision)

    """ 結果 """
    for a in qtree:
        print "%s %s %s %s" % (a.x1, a.y1, a.x2, a.y2),
        for p in a.points():
            print p,
        print
