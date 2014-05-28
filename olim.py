import numpy
import math
from lib.quadtree import Quadtree
from lib.util import Util

class Window:
    def __init__(self, N):
        self.values = {}
        self.n = {}
        self.N = N

    def count(self, w):
        if w in self.n:
            return self.n[w]
        else:
            return 0

    def append(self, w, k):
        if w in self.values:
            if self.n[w] > self.N:
                print 'window overflow'
                exit()
            self.values[w].append(k)
            self.n[w] += 1
        else:
            self.values[w] = [k]
            self.n[w] = 1

    def pop(self, w):
        if w in self.values:
            if self.n[w] == 0:
                print 'window underflow'
                exit()
            self.n[w] -= 1
            return self.values[w].pop(0)
        else:
            print 'window no such word to pop'
            exit()

class WordDistribution:
    def __init__(self, N):
        self.values = {}
        self.N = N

    def get(self,w):
        if w in self.values:
            return self.values[w]
        else:
            return None

    def inc(self,w,l):
        if w in self.values:
            if l in self.values[w]:
                if self.values[w][l] <= self.N:
                    self.values[w][l] += 1
                else:
                    print 'WD overflow'
                    exit()
            else:
                self.values[w][l] = 1
        else:
            self.values[w] = {}
            self.values[w][l] = 1

    def dec(self,w,l):
        if w in self.values:
            if self.values[w][l] > 0:
                self.values[w][l] -= 1
            else:
                print 'WD underflow'
                exit()
        else:
            print 'WD no such word to dec'
            exit()

class UserDistribution:
    def __init__(self, N):
        self.values = {}
        self.N = N

    def get(self, u):
        if u in self.values:
            return self.values[u]
        else:
            return None

    def update(self, u, wd):
        if u in self.values:
            for i in wd.keys():
                if not i in self.values[u]:
                    self.values[u][i] = wd[i]
                else:
                    self.values[u][i] += wd[i]
        else:
            self.values[u] = {}
            for i in wd.keys():
                self.values[u][i] = wd[i]

class KL:
    def __init__(self, N, population):
        self.values = {}
        self.N = N
        self.population = population

    def get(self, w):
        if w in self.values:
            return self.values[w]
        else:
            print 'KL: no such word with calculated KL'
            exit()

    def calc(self, w, wd):
        s = 0
        for i in self.population.keys():
            if i in wd:
                pi = wd[i] / float(self.N)
                s += pi * ( math.log(pi) - math.log(self.population[i]) )
        self.values[w] = s

    def update(self, w, i, j, wd):
        if w in self.values:
            ni = wd[i]
            nj = wd[j]
            qi = self.population[i]
            qj = self.population[j]
            prev = self.values[w]
            if ni-1 > 0:
                prev += (1/float(self.N)) * ( ni * math.log(ni) - (ni-1) * math.log(ni-1) - math.log(self.N * qi) )
            else:
                prev += (1/float(self.N)) * ( -math.log(self.N * qi) )
            if nj > 0:
                prev += (1/float(self.N)) * ( nj * math.log(nj) - (nj+1) * math.log(nj+1) + math.log(self.N * qj) )
            else:
                prev += (1/float(self.N)) * math.log(self.N * qj)
            self.values[w] = prev
        else:
            print "KL: no such word to update"
            exit()

class OLIM:
    def __init__(self, users, tweets, params):
        self.users = users
        self.tweets = tweets
        self.params = params

    def number_of_users(self):
        return len(self.users)

    def geoPartitioning(self,params):
        """ make data """
        data = []
        for u in self.users.iter():
            if u['location'] != None:
                data.append(u['location'])

        """ partition """
        qtree = Quadtree(data,params['x1'],params['y1'],params['x2'],params['y2'],params['maxpoints'],params['maxdivision'])

        """ return the areas """
        return qtree

    def make_population(self, qtree):
        population = {}
        for a in qtree:
            i = a.aid
            population[i] = float(a.number_of_points) / self.number_of_users()
        return population

    def updateKL(self, user, l, words):
        for w in words:
            self.window.append(w, l)
            self.wd.inc(w, l)
            if self.window.count(w) == self.params['N']:
                wd = self.wd.get(w)
                self.kl.calc(w, wd)
            elif self.window.count(w) > self.params['N']:
                pl = self.window.pop(w)
                self.wd.dec(w, pl)
                if l != pl:
                   self.kl.update(w, l, pl, self.wd.get(w))

    def updateUD(self, user, words, dmin):
        for w in words:
            if self.window.count(w) == self.params['N']:
                if self.kl.get(w) > dmin:
                    self.ud.update(user['id'], self.wd.get(w))

    def infer(self, qtree):
        self.ud = UserDistribution(self.params['N'])
        self.wd = WordDistribution(self.params['N'])
        self.window = Window(self.params['N'])
        self.kl = KL(params['N'], self.make_population(qtree))
        for tweet in self.tweets.stream():
            if type(tweet) == type({}) and 'timestamp' in tweet:
                user = self.users.get(tweet['user_id'])
                if user != None:
                    cl = user['location'] # user who posts this tweet
                    words = set(Util.get_nouns(tweet['text'], self.params['lang'])) # words contained in this tweet
                    if cl != None:
                        """ labeled user """
                        self.updateKL(user, qtree.get_area_id(cl), words)
                    else:
                        """ unlabeled user """
                        self.updateUD(user, words, self.params['dmin'])

        """ Location prediction using user distribution """
        for user in self.users.iter():
            if user['location'] == None:
                """ unlabeled user """
                ud = self.ud.get(user['id'])
                if ud != None:
                    """ at least one observation """
                    inferred_location_number = self.predict(ud)
                    inferred_location_coordinates = self.leaves[inferred_location_number].center
                    user['location'] = inferred_location_coordinates

    def predict(self, ud):
        B = numpy.array(self.population)
        for k in ud:
            B[int(k)] += ud[k]
        return B.argmax()

    def get_users(self):
        return self.users

if __name__ == '__main__':
    import sys
    import pickle
    import json
    import os
    from lib.db import DB
    from lib.users import Users
    from lib.tweets_db import Tweets

    def load_params(filepath):
        f = open(filepath, 'r')
        params = json.loads(f.read().rstrip())
        f.close()
        return params

    def evaluate(inferred, answer):
        for u in answer.iter():
            v = inferred.get(u['id'])
            if v['location'] != None:
                print Util.hubeny_distance(v['location'], u['location'])

    if len(sys.argv) < 7:
        print '[usage]: python %s [training set] [test set] [params] [db user name] [db pass] [db name]' % sys.argv[0]
        exit()

    training = Users()
    training.load_file(sys.argv[1])
    test = Users()
    test.load_file(sys.argv[2])

    params = load_params(sys.argv[3])

    db = DB(sys.argv[4], sys.argv[5], sys.argv[6])
    tweets = Tweets(db)

    olim = OLIM(training, tweets, params)

    """ quadtree partitioning """
    qtree = olim.geoPartitioning(params)

    """ infer """
    olim.infer(qtree)
    inferred = olim.get_users()

    """ evaluate """
    evaluate(inferred, test)
