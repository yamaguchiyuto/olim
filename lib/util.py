# -*- coding: utf-8 -*-
import math
import re
import time
import MeCab
import nltk

class Util:
    tagger = MeCab.Tagger('-Ochasen')

    @classmethod
    def remove_usernames_and_urls(self, text):
        username_removed_text = re.sub('@\w+', '', text) # remove usernames
        return re.sub('(https?|ftp)(:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)', '', username_removed_text) # remove urls

    @classmethod
    def get_nouns(self, text_str, lang):
        if lang == 'en':
            return self.get_nouns_en(text_str)
        elif lang == 'ja':
            return self.get_nouns_ja(text_str)
        else:
            print 'invalid language'
            exit()

    @classmethod
    def get_nouns_ja(self, text):
        words = []
        node = self.tagger.parseToNode(self.remove_usernames_and_urls(text))
        while node:
            if node.feature.split(',')[0] == '名詞':
                words.append(node.surface)
            node = node.next
        return words

    @classmethod
    def get_nouns_en(self, text_str):
        text = nltk.word_tokenize(text_str)
        result = nltk.tag.pos_tag(text)
        nouns = [r[0]  for r in result if r[1] in {'NNP', 'NNPS'}]
        return nouns


    @classmethod
    def calc_medoid(self, points):
        min_d = -1
        medoid = [-1,-1]
        for p in points:
            s = 0
            for q in points:
                d = self.distance(p, q)
                s += d
            if s < min_d or min_d == -1:
                min_d = s
                medoid = p
        return medoid


    @classmethod
    def calc_centroid(self, points):
        xsum = sum([p[0] for p in points])
        ysum = sum([p[1] for p in points])
        return (xsum/len(points), ysum/len(points))

    @classmethod
    def rad(self, x):
        return x * math.pi / 180

    @classmethod
    def hubeny_distance(self, p, q):
        latd = self.rad(p[0] - q[0])
        longd = self.rad(p[1] - q[1])
        latm = self.rad(p[0] + q[0]) / 2
        a = 6377397.155
        b = 6356079.000
        e2 = 0.00667436061028297
        W = math.sqrt(1 - e2 * math.sin(latm)**2)
        M = 6334832.10663254 / W**3
        N = a / W
        d = math.sqrt((latd*M)**2 + (longd*N*math.cos(latm))**2)
        return d
