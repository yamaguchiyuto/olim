# -*- coding: utf-8 -*-
class Quadtree:
    def __init__(self,data,x1,y1,x2,y2,maxpoints,maxdivision):
        self.data = data
        self.sequential_id = 0
        self.leaves = {}
        self.root = self.divide(self.init_area(data,x1,y1,x2,y2),maxpoints,maxdivision)

    def __iter__(self):
        for aid in self.leaves:
            yield self.leaves[aid]

    def init_area(self,data,x1,y1,x2,y2):
        initial = Area(x1,y1,x2,y2)
        for d in data:
            initial.append(d)
        return initial

    def subdivide(self,area):
        division = []

        """ 分割後の各辺の長さ """
        xl = (area.x2 - area.x1)/2
        yl = (area.y2 - area.y1)/2

        """ 分割後の領域を生成 """
        for dx in [0,1]:
            for dy in [0,1]:
                """
                0 2
                1 3
                の順番
                """
                sub_area = Area(area.x1+dx*xl, area.y1+dy*yl, area.x1+(1+dx)*xl, area.y1+(1+dy)*yl)
                division.append(sub_area)

        """ 分割前の領域に属すデータ点を分割後の領域にアサイン """
        for p in area.points():
            for sub_area in division:
                if sub_area.cover(p):
                    sub_area.append(p)
                    break

        return division

    def divide(self, area, maxpoints, division_left):
        """ 引数で与えられたdivision_left回だけ分割を繰り返す """
        if division_left == 0 or area.number_of_points() <= maxpoints:
            """ areaに含まれるデータ点の数がmaxpointsを超えていなければ分割終了 """
            area.set_fixed(self.sequential_id)
            area.calc_center() # areaに属すデータ点のセントロイドを計算
            area.set_id(self.sequential_id)
            self.leaves[self.sequential_id] = area
            self.sequential_id += 1
            return area
        else:
            """ areaに含まれるデータ点の数がmaxpointsを超えていれば四分割 """
            next_level = self.subdivide(area)
            """ 子エリアそれぞれを更に分割 """
            for i in range(4):
                child = self.divide(next_level[i],maxpoints,division_left-1)
                area.set_child(i,child)
            """ 分割後のエリアを返す """
            return area

    def get_area_id(self,p):
        return self.root.covered(p)

class Area:
    def __init__(self,x1,y1,x2,y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.points_ = []
        self.fixed = False
        self.center = None
        """
        0 2
        1 3
        """
        self.children = [None,None,None,None]

    def calc_center(self):
        if self.number_of_points() == 0:
            self.center = (self.x1 + (self.x2-self.x1)/2, self.y1 + (self.y2-self.y1)/2)
        else:
            sumx = 0.
            sumy = 0.
            for p in self.points_:
                sumx += p[0]
                sumy += p[1]
            self.center = (sumx/len(self.points_), sumy/len(self.points_))

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

    def set_fixed(self,aid):
        """ 分割が終わったフラグを立てる """
        self.fixed = True
        """ エリアにIDを付ける """
        self.aid = aid

    def set_id(self,aid):
        self.aid = aid

    def set_child(self,n,area):
        self.children[n] = area

    def covered(self,p):
        if self.cover(p):
            if self.fixed:
                return self.aid
            else:
                """ 子エリアのIDを計算 """
                cid = 0
                if self.x1 + (self.x2 - self.x1) / 2 < p[0]:
                    """ Right """
                    cid += 2
                if self.y1 + (self.y2 - self.y1) / 2 < p[1]:
                    """ Down """
                    cid += 1
                return self.children[cid].covered(p)
        else:
            return None

    def cover(self, p):
        """ あるデータ点pがこの領域にカバーされるかどうか """
        if self.x1 < p[0] and self.y1 < p[1] and self.x2 >= p[0] and self.y2 >= p[1]:
            return True
        else:
            return False

if __name__ == '__main__':
    import sys

    def read_data(file_name):
        data = []
        for line in open(file_name, 'r'):
            entries = line.rstrip().split(' ')
            lat = float(entries[0])
            lng = float(entries[1])
            data.append((lat,lng))
        return data

    x1 = float(sys.argv[1])
    y1 = float(sys.argv[2])
    x2 = float(sys.argv[3])
    y2 = float(sys.argv[4])
    maxpoints = int(sys.argv[5])
    maxdivision = int(sys.argv[6])
    data = read_data(sys.argv[7])

    """ 分割 """
    qtree = Quadtree(data,x1,y1,x2,y2,maxpoints,maxdivision)

    """ 結果 """
    for a in qtree:
        print a.aid,a.x1,a.y1,a.x2,a.y2,a.center

    p = (0.37,0.55)
    print p,qtree.get_area_id(p)

