# -*- coding: utf-8 -*-
import sys

class Quadtree:
    def __init__(self,data,x1,y1,x2,y2):
        self.data = data
        self.areas = self.init_area(data,x1,y1,x2,y2)
        self.assign = self.init_assign(data)

    def init_assign(self,data):
        assign = {}
        for uid in data:
            assign[uid] = -1
        return assign

    def init_area(self,data,x1,y1,x2,y2):
        initial = Area(x1,y1,x2,y2,0)
        for uid in data:
            initial.append(data[uid])
        return [initial]

    def covered(self,uid):
        return self.assign[uid]

    def divide(self,area,level):
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

    def quadtree(self, maxpoints, maxdivision):
        """ 引数で与えられたmaxdivision回だけ分割を繰り返す """
        for n in range(maxdivision):
            new_areas = []
            for i in range(len(self.areas)):
                if not self.areas[i].is_fixed():
                    """ まだ分割が終わっていない領域に対して """
                    if self.areas[i].number_of_points() > maxpoints:
                        """ 領域に属すデータ点の数がmaxpoints個を超えていたら分割 """
                        division = self.divide(self.areas[i],n+1)
                        for d in division:
                            new_areas.append(d)
                    else:
                        """ 領域に属すデータ点の数がmaxpoints個を超えていなかったらもう分割しない """
                        self.areas[i].set_fixed()
                        new_areas.append(self.areas[i])
                else:
                    """ 分割が終わっていればそのまま """
                    new_areas.append(self.areas[i])
            self.areas = new_areas

        """ データ点がどのエリアにアサインされているかのインデックスを作る """
        self.make_assign()

    def make_assign(self):
        for uid in self.data:
            for i in range(len(self.areas)):
                if self.areas[i].cover(data[uid]):
                    break
            self.assign[uid] = i

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

    def number_of_points(self):
        return len(self.points_)

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

def read_data(file_name):
    data = {}
    for line in open(file_name, 'r'):
        entries = line.rstrip().split(' ')
        uid = int(entries[0])
        lat = float(entries[1])
        lng = float(entries[2])
        data[uid] = (lat,lng)
    return data

if __name__ == '__main__':
    x1 = float(sys.argv[1])
    y1 = float(sys.argv[2])
    x2 = float(sys.argv[3])
    y2 = float(sys.argv[4])
    maxpoints = int(sys.argv[5])
    maxdivision = int(sys.argv[6])
    data = read_data(sys.argv[7])

    """ 分割 """
    qtree = Quadtree(data,x1,y1,x2,y2)
    qtree.quadtree(maxpoints, maxdivision)

    """ 結果 """
    for a in qtree.areas:
        print "%s %s %s %s" % (a.x1, a.y1, a.x2, a.y2),
        for p in a.points():
            print p,
        print

    for uid in data:
        print uid,qtree.covered(uid)
