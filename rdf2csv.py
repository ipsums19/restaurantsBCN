#!/usr/bin/python

import sys

from HTMLParser import HTMLParser

allrest=[]

class address(object):

    def __init__(self):
        self.street = ""
        self.district = ""
        self.neighborhood = ""
        self.postal_code = ""
        self.locality = ""

    def __str__(self):
        return "(address) %s" % ", ".join([self.street, self.postal_code, self.neighborhood, self.district, self.locality])

class telefon(object):

    def __init__(self):
        self.nombre = ""
        self.tipus = "Tel"

    def __str__(self):
        return "(telefon) %s: %s" % (self.tipus, self.nombre)

class email(object):

    def __init__(self):
        self.email = ""
        self.tipus = "Email"

    def __str__(self):
        return "(email) %s: %s" % (self.tipus, self.email)


class restaurant(object):

    def __init__(self):
        self.nom = ""
        self.adaptat = "0"
        self.lat = 0.
        self.lon = 0.
        self.addr = None
        self.telfs = []
        self.emails = []
        self.url = ""

    def afegir_nom(self,nom):
        self.nom = nom

    def afegir_adaptat(self, adaptat):
        self.adaptat = adaptat

    def afegir_adreca(self, addr):
        self.addr = addr

    def afegir_url(self, url):
        self.url = url

    def afegir_tlf(self, tlf):
        self.telfs.append(tlf)

    def afegir_lat(self, lat):
        self.lat = float(lat)

    def afegir_lon(self, lon):
        self.lon = float(lon)

    def afegir_email(self, email):
        self.emails.append(email)

    def as_csv_row(self):
        email = ""
        if self.emails:
            email = self.emails[0]
        telf = ""
        fax = ""
        if self.telfs:
            faxs = [x for x in self.telfs if x.tipus == "Fax"]
            if faxs:
                fax = faxs[0]
            telf = self.telfs[0]
        return "\t".join([self.nom,
            self.adaptat,
            str(self.lat),
            str(self.lon),
            str(email)[8:],
            str(telf)[10:],
            str(fax)[10:],
            str(self.addr)[10:],
            self.url])

    def __str__(self):
        s = "(restaurant) %s\n" % self.nom
        s += "\tadaptat: %s\n" % self.adaptat
        s += "\tlatitude: %s\n" % self.lat
        s += "\tlongitude: %s\n" % self.lon
        s += "\temails:\n"
        for e in self.emails:
            s += "\t\t%s\n" % e
        s += "\ttelefons:\n"
        for e in self.telfs:
            s += "\t\t%s\n" % e
        s += "\taddress: %s\n" % self.addr
        s += "\turl: %s\n" % self.url
        return s

def get_attr(attrs, name):
    d = dict(attrs)
    return d[name]

# creem una subclasse i sobreescribim el metodes del han
class MHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.crest = None
        self.caddr = None
        self.ctlf = None
        self.cemail = None
        self.ctag = ""

    def handle_starttag(self, tag, attrs):
        self.ctag = tag
        if tag == 'v:vcard':
            self.crest = restaurant()
        elif tag == 'v:address':
            self.caddr = address()
        elif tag == 'v:url':
            self.crest.afegir_url(get_attr(attrs, 'rdf:resource'))
        elif tag == 'v:tel':
            self.ctlf = telefon()
        elif tag == 'v:email':
            self.cemail = email()
        # telf stuff
        elif tag == 'rdf:type' and self.ctlf is not None:
            data = get_attr(attrs, 'rdf:resource')
            data = data[data.index("#") + 1:]
            self.ctlf.tipus = data
        # email stuff
        elif tag == 'rdf:description' and self.cemail is not None:
            data = get_attr(attrs, 'rdf:about')
            data = data[data.index(":") + 1:]
            self.cemail.email = data
        elif tag == 'rdf:type' and self.cemail is not None:
            data = get_attr(attrs, 'rdf:resource')
            data = data[data.index("#") + 1:]
            self.cemail.tipus = data

    def handle_endtag(self, tag):
        self.ctag = ""
        if tag == 'v:vcard':
            allrest.append(self.crest)
            self.crest = None
        elif tag == 'v:address':
            self.crest.afegir_adreca(self.caddr)
            self.caddr = None
        elif tag == 'v:tel':
            self.crest.afegir_tlf(self.ctlf)
            self.ctlf = None
        elif tag == 'v:email':
            self.crest.afegir_email(self.cemail)
            self.cemail = None

    def handle_data(self, data):
        if self.ctag == 'v:fn':
            self.crest.afegir_nom(data)
        elif self.ctag == 'xv:adapted':
            self.crest.afegir_adaptat(data)
        elif self.ctag == 'v:latitude':
            self.crest.afegir_lat(data)
        elif self.ctag == 'v:longitude':
            self.crest.afegir_lon(data)
        # telefon stuff
        elif self.ctag == 'rdf:value' and self.ctlf is not None:
            self.ctlf.nombre = data
        # address stuff
        elif self.ctag == 'v:street-address' and self.caddr is not None:
            self.caddr.street = data
        elif self.ctag == 'xv:district' and self.caddr is not None:
            self.caddr.district = data
        elif self.ctag == 'xv:neighborhood' and self.caddr is not None:
            self.caddr.neighborhood = data
        elif self.ctag == 'v:postal-code' and self.caddr is not None:
            self.caddr.postal_code = data
        elif self.ctag == 'v:locality' and self.caddr is not None:
            self.caddr.locality = data


f = open('restaurants.rdf', 'rb') # obre l'arxiu
rdfSource = f.read()

parser = MHTMLParser()
parser.feed(rdfSource)
print "\t".join(["nom", "adaptat", "lat", "lon", "email", "telf", "fax", "addr", "url"])
for r in allrest:
    print r.as_csv_row()
