import sys

def median(distances):
    return distances[len(distances)/2]

def precision(distances, d):
    c = 0
    for distance in distances:
        if distance < d:
            c += 1
    return float(c) / len(distances)



distances = []
for line in open(sys.argv[1], 'r'):
    e = float(line.rstrip())
    distances.append(e)

distances.sort()
print median(distances)
print precision(distances, 160000)
