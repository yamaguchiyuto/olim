import numpy
import math
import datetime
from sklearn import mixture
from lib.util import Util

class Window:
    def __init__(self, N):
        self.values = {} # tuple (location,time) inside
        self.n = {}
        self.N = N
        self.oldest_time = {}

    def count(self, w):
        if w in self.n:
            return self.n[w]
        else:
            return 0

    def append(self, w, location, current_time):
        if w in self.values:
            if self.n[w] > self.N:
                print 'window overflow'
                exit()
            self.values[w].append((location,current_time))
            self.n[w] += 1
        else:
            self.values[w] = [(location,current_time)]
            self.n[w] = 1
            self.oldest_time[w] = current_time

    def pop(self, w):
        if w in self.values:
            if self.n[w] == 0:
                print 'window underflow'
                exit()
            self.n[w] -= 1
            self.oldest_time[w] = self.values[w][1][1]
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

    def geoPartitioning(self):
        """ make data """
        data = []
        for u in self.users.iter():
            if u['location'] != None:
                data.append(u['location'])

        """ fitting parameters """
        gmm = mixture.GMM(n_components = self.params['K'])
        gmm.fit(data)

        """ return the model """
        return gmm

    def make_population(self, weights):
        population = {}
        i = 0
        for v in weights:
            population[str(i)] = v
            i += 1
        return population 

    def updateKL(self, user, user_location, current_time, words):
        for w in words:
            """ append location and current time to the window """
            self.window.append(w, user_location, current_time)
            self.wd.inc(w, user_location)
            if self.window.count(w) == self.params['N']:
                wd = self.wd.get(w)
                self.kl.calc(w, wd)
            elif self.window.count(w) > self.params['N']:
                removed_location,oldest_time = self.window.pop(w)
                self.wd.dec(w, removed_location)
                if user_location != removed_location:
                    """ If added location and removed location is not same """
                    self.kl.update(w, user_location, removed_location, self.wd.get(w))

    def updateUD(self, user, words, current_time, dmin):
        for w in words:
            if self.window.count(w) == self.params['N']:
                if self.kl.get(w) > dmin:
                    """ if kl value larger than threshold """
                    oldest_time = self.window.oldest_time[w]
                    if current_time - oldest_time < datetime.timedelta(seconds=self.params['window_th']):
                        """ if not too long window """
                        print w,current_time,oldest_time,current_time-oldest_time,self.kl.get(w)
                        self.ud.update(user['id'], self.wd.get(w))

    def infer(self, model):
        self.ud = UserDistribution(self.params['N'])
        self.wd = WordDistribution(self.params['N'])
        self.window = Window(self.params['N'])
        self.kl = KL(params['N'], self.make_population(model.weights_))
        for tweet in self.tweets.stream():
            if type(tweet) == type({}) and 'timestamp' in tweet:
                user = self.users.get(tweet['user_id'])
                current_time = tweet['timestamp']
                if user != None:
                    user_location = user['location'] # user who posts this tweet
                    words = set(Util.get_nouns(tweet['text'], self.params['lang'])) # words contained in this tweet
                    if user_location != None:
                        """ labeled user """
                        user_location = str(model.predict([user_location])[0])
                        self.updateKL(user, user_location, current_time, words)
                    else:
                        """ unlabeled user """
                        self.updateUD(user, words, current_time, self.params['dmin'])

        """ Location prediction using user distribution """
        for user in self.users.iter():
            if user['location'] == None:
                """ unlabeled user """
                ud = self.ud.get(user['id'])
                if ud != None:
                    """ at least one observation """
                    inferred_location_number = self.predict(ud, model)
                    inferred_location_coordinates = model.means_[inferred_location_number]
                    user['location'] = inferred_location_coordinates

    def predict(self, ud, model):
        B = numpy.array(model.weights_)
        for k in ud:
            B[int(k)] += ud[k]
        return B.argmax()

    def get_users(self):
        return self.users

if __name__ == '__main__':
    import sys
    import pickle
    import json
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

    if len(sys.argv) < 8:
        print '[usage]: python %s [training set] [test set] [params] [db user name] [db pass] [db name] [model]' % sys.argv[0]
        print 'Specify model file even if there does not exist, to save the geoPartitioning result.'
        exit()

    training = Users()
    training.load_file(sys.argv[1])
    test = Users()
    test.load_file(sys.argv[2])

    params = load_params(sys.argv[3])

    db = DB(sys.argv[4], sys.argv[5], sys.argv[6])
    tweets = Tweets(db)

    olim = OLIM(training, tweets, params)

    try:
        f = open(sys.argv[7], 'r')
    except IOError:
        model = olim.geoPartitioning()
        f = open(sys.argv[7], 'w')
        pickle.dump(model, f)
        f.close()
    else:
        model = pickle.load(f)
        f.close()

    olim.infer(model)
    inferred = olim.get_users()
    evaluate(inferred, test)
