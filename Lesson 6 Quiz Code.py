
# coding: utf-8

# In[2]:

#QUIZ 1

import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
        # MY CODE HERE
        tags = {}
        for event, elem in ET.iterparse(filename):
            if elem.tag not in tags.keys():
                tags[elem.tag]=1
            else:
                tags[elem.tag]=tags[elem.tag]+1
        return tags


def test():

    tags = count_tags('example.osm')
    pprint.pprint(tags)
    assert tags == {'bounds': 1,
                     'member': 3,
                     'nd': 4,
                     'node': 20,
                     'osm': 1,
                     'relation': 1,
                     'tag': 7,
                     'way': 1}


# In[3]:

#QUIZ 2

import xml.etree.cElementTree as ET
import pprint
import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# MY CODE HERE
def key_type(element, keys):
    if element.tag == "tag":
        k = element.attrib['k']
        if re.search(lower,k):
            keys['lower']+=1
        elif re.search(lower_colon,k):
            keys['lower_colon']+=1
        elif re.search(problemchars,k):
            keys['problemchars']+=1
        else:
            keys['other']+=1
    return keys



def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys



def test():
    keys = process_map('example.osm')
    pprint.pprint(keys)
    assert keys == {'lower': 5, 'lower_colon': 0, 'other': 1, 'problemchars': 1}


# In[4]:

#QUIZ 3

import xml.etree.cElementTree as ET
import pprint
import re

def get_user(element):
    return

#MY CODE HERE
def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if element.get('uid'):
            users.add(element.get('uid'))

    return users


def test():

    users = process_map('example.osm')
    pprint.pprint(users)
    assert len(users) == 6


# In[5]:

#QUIZ 4

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "example.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# MY CODE HERE
mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd.": "Road"
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types

# MY CODE HERE
def update_name(name, mapping):
    work =[]
    words = re.findall(re.compile("\S+"),name)
    for word in words:
        if word in mapping.keys():
            work.append(mapping[word])
        else:
            work.append(word)
    name=" ".join(work)
    
    return name


def test():
    st_types = audit(OSMFILE)
    assert len(st_types) == 3
    pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
            if name == "West Lexington St.":
                assert better_name == "West Lexington Street"
            if name == "Baldwin Rd.":
                assert better_name == "Baldwin Road"


# In[6]:

#QUIZ 5

import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

# MY CODE HERE
def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        created = {}
        lat = None
        lon = None
        node_refs = []
        address = {}
        for i in element.attrib:
            if i in CREATED:
                created[i]=element.attrib[i]
            elif i=='lat':
                lat = float(element.attrib[i])
            elif i=='lon':
                lon = float(element.attrib[i])
            else:
                node[i]=element.attrib[i]
        node['created']=created 
        node['pos']=[lat,lon]
        node['type']=element.tag
        for child in element:
            if child.tag == "tag":
                k = child.attrib['k']
                v = child.attrib['v']
                if re.search(problemchars,k):
                    continue
                elif k.startswith('addr:'):
                    if re.search(re.compile(":"),k[5:]):
                        continue
                    else:
                        address[k[5:]]=v
                else:
                    node[k]=v
            if child.tag == "nd":
                node_refs.append(child.attrib['ref'])
        if node_refs:
            node['node_refs']=node_refs
        if address:
            node['address']=address

        print node
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    data = process_map('example.osm', True)
    correct_first_elem = {
        "id": "261114295", 
        "visible": "true", 
        "type": "node", 
        "pos": [41.9730791, -87.6866303], 
        "created": {
            "changeset": "11129782", 
            "user": "bbmiller", 
            "version": "7", 
            "uid": "451048", 
            "timestamp": "2012-03-28T18:31:23Z"
        }
    }
    assert data[0] == correct_first_elem
    assert data[-1]["address"] == {
                                    "street": "West Lexington St.", 
                                    "housenumber": "1412"
                                      }
    assert data[-1]["node_refs"] == [ "2199822281", "2199822390",  "2199822392", "2199822369", 
                                    "2199822370", "2199822284", "2199822281"]

