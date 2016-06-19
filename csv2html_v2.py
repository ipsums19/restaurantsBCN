import csv
import xml.etree.ElementTree as ET
import urllib
from math import radians, cos, sin, asin, sqrt

def parse(query):
    if type(query) is tuple:
        if query:
            res = parse(query[0]).copy()
        for q in query[1:]:
            res &= parse(q)
        return res
    elif type(query) is list:
        res = set()
        for q in query:
            res |= parse(q)
        return res
    elif type(query) is str:
        query = query.lower()
        if query not in reverse_index:
            return set()
        return reverse_index[query.lower()]


index = []
reverse_index = {}
header = None
with open("restaurants.csv", "r") as data:
    reader = csv.reader(data, delimiter="\t")
    header = next(reader)
    id = 0
    for r in reader:
        index.append(r)
        words = r[0].lower().split()
        for w in words:
            if w not in reverse_index:
                reverse_index[w] = set()
            reverse_index[w].add(id)
        id += 1


    print """<html>
<head><title>Tabla</title></head>
<body>"""

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2, = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km
xmltext = urllib.urlopen("http://wservice.viabicing.cat/v1/getstations.php?v=1")
root = ET.fromstring(xmltext.read())

while True:
    try:
        query = input()
    except:
        break

    if type(query) is str:
        try:
            query = eval(query)
        except:
            pass

    print "<h1>%s</h1>" % str(query)
    print "<table border=\"1\">"
    print "<tr>"
    for i in header:
        print "  <td><strong>" + i + "</strong></td>"
    print "  <td><strong>" + " Bicis Disponibles" + "</strong></td>"
    print "  <td><strong>" + " Places Lliures " + "</strong></td>"
    print "</tr>"
    result = parse(query)
    for id in result:
        print "<tr>"
        for i in index[id]:
            print "  <td>" + i + "</td>"
        lat = index[id][2]
        lon = index[id][3]
        bicis = []
        parking = []
        for child in root:
            if child.tag == "station":
                m = haversine(float(lat), float(lon), float(child[2].text), float(child[3].text)) * 1000
                if m < 1000:
                    if float(child[9].text) > 0:
                        parking.append([child[4].text, m])
                    if float(child[10].text) > 0:
                        bicis.append([child[4].text, m])
        bicis.sort(key = lambda x: x[1])
        parking.sort(key = lambda x: x[1])
        print "  <td>"
        for bici in bicis:
            print "    " + bici[0]
        print "</td>"

        print "  <td>"
        for park in parking:
            print "    " + park[0]
        print "</td>"

        print "</tr>"
    print "</table>"

print "</body>","</html>"

