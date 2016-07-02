
# coding: utf-8

# In[2]:

import pymongo
import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict
import codecs
import json


# In[14]:

data = "E:\Udacity\Project 3 - OpenStreetMap\New Haven Data"
osm_data = open("E:\Udacity\Project 3 - OpenStreetMap\New Haven Data", "r")
tree = ET.parse("E:\Udacity\Project 3 - OpenStreetMap\New Haven Data")
clean_data = "E:\Udacity\Project 3 - OpenStreetMap\Clean New Haven Data.xml"


# In[4]:

problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


# In[15]:

# Produce a count of how many tag types are in the document
def count_tags(filename):
        tags = {}
        for event, elem in ET.iterparse(filename):
            if elem.tag not in tags.keys():
                tags[elem.tag]=1
            else:
                tags[elem.tag]=tags[elem.tag]+1
        return tags


# In[16]:

print count_tags(osm_data)


# In[17]:

street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)
street_types = defaultdict(int)
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

#Counts the number of each type of street
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        street_types[street_type] += 1
        
# Checks if an element's tag contains a street name
def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")


# In[18]:

def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print "%s: %d" % (k,v)


# In[19]:

#Prints a list of the different type of streets in the dataset with a count for each
#Shows any errors in the types of street or lack of street type in the street name
def audit_street_name(filename):
    for event, elem in ET.iterparse(filename):
        if is_street_name(elem):
            audit_street_type(street_types, elem.attrib['v'])
    print_sorted_dict(street_types)


# In[20]:

audit_street_name(data)


# In[25]:

#Creates a list of every unique 'k' tag in the file
def unique_k_tags(filename):
        tags = set()
        for event, elem in ET.iterparse(filename):
            if elem.tag == "tag":
                tags.add(elem.attrib['k'])
        return tags


# In[26]:

#unique_k_tags(data)


# In[29]:

#Limits the elements being checked to those with a 'tag' tag and string value in the 'k' tag
def is_tag_type(elem, tag):
    return (elem.tag == "tag") and (elem.attrib['k'] == str(tag))

#Produces a list of values and their frequency in the data for a given 'k' tag 
def audit_k_tag(filename, tag):
    tag_types = defaultdict(int)
    for event, elem in ET.iterparse(filename):
        if is_tag_type(elem,tag):
            tag_types[elem.attrib['v']] += 1
    print_sorted_dict(tag_types)


# In[30]:

#audit_k_tag(data,'amenity')


# In[31]:

#Returns a set of unique users in the dataset
def process_map_1(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if element.get('uid'):
            users.add(element.get('uid'))

    return users


# In[32]:

print "Total # of Unique Users in the Dataset: " + str(len(process_map_1(data)))


# In[33]:

#Map for the cleaning of street types and names
mapping = { "College": "College Street",
            "Colledge Street": "College Street",
            "church": "Church",
            "Blvd": "Boulevard",
            "Ave": "Avenue",
            "Rd": "Road",
            "St": "Street",
            "street": "Street",
            }


# In[34]:

#Checks if a given street type exists within the list of acceptable values
def street_error(street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            return True

#Identifies urls that do not start with 'http'
def url_error(url):
    if url.startswith('http'):
        return False
    else:
        return True


    


# In[48]:

#Various checks of formatting to be used in the identification of errant values that will require cleaning
number_only = re.compile('^[\d]+$')
nums_and_letters = re.compile('^[a-zA-Z\d-]+$')
mph_only = re.compile('^[\d]+\smph$')
phone_format = re.compile('\d{3}-\d{3}-\d{4}')
phone_with_plus = re.compile('\+\d\s\d{3}\s\d{7}')
phone_with_paren = re.compile('\(\d{3}\)\s\d{3}-\d{4}')
phone_full_10 = re.compile('\d{10}')
phone_with_dots = re.compile('\d{3}\.\d{3}\.\d{4}')


# In[35]:

#Produces a report of the number errors for each type of tag that is being audited
def report_data(filename):

    house_numbers = 0
    post_codes = 0
    street_names = 0
    capacity = 0
    population = 0
    state = 0
    fax = 0
    phone = 0
    speed = 0
    website = 0
    place_name = 0
    wood = 0
    drinkable = 0
    direct = 0
    for _, elem in ET.iterparse(filename):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                k = tag.attrib['k']
                v = tag.attrib['v']
                if k == 'addr:housenumber':
                    if re.search(nums_and_letters,v):
                        continue
                    else:
                        house_numbers+=1
                elif k == 'addr:postcode':
                    if re.search(number_only,v):
                        continue
                    else:
                        post_codes+=1
                        
                elif k=='addr:street':
                    if street_error(v):
                        #A unique exception to the rules for the rest of the streets in the dataset
                        if v=='Broadway':
                            continue
                        else:
                            street_names+=1
                elif k=='capacity':
                    if re.search(number_only,v):
                        continue
                    else:
                        capacity+=1
                elif k=='census:population':
                    if re.search(number_only,v):
                        continue
                    else:
                        population+=1
                elif k=='addr:state':
                    if len(v)>2:
                        state+=1
                elif k=='fax':
                    if re.search(phone_format,v):
                        continue
                    else:
                        fax+=1
                elif k=='phone':
                    if re.search(phone_format,v):
                        continue
                    else:
                        phone+=1
                elif k=='maxspeed':
                    if re.search(mph_only,v):
                        continue
                    else:
                        speed+=1
                elif k=='website':
                    if url_error(v):
                        website+=1
                elif k=='place_name':
                    place_name+=1
                elif k=='wood':
                    wood+=1
                elif k=='drinkable':
                    drinkable+=1
                elif k=='Direct mailing':
                    direct+=1
                
    print "Number of Errors Among the Following \'K\' tags"
    print "addr:housenumber : " + str(house_numbers)
    print "addr:postcode : " + str(post_codes)
    print "addr:street : " + str(street_names)
    print "capacity : " + str(capacity)
    print "census:population : " + str(population)
    print "addr:state : " + str(state)
    print "fax : " + str(fax)
    print "phone : " + str(phone)
    print "maxspeed : " + str(speed)
    print "website : " + str(website)
    print "place_name : " + str(place_name)
    print "wood : " + str(wood)
    print "drinkable : " + str(drinkable)
    print "Direct Mailing : " + str(direct)

    


# In[50]:

report_data(data)


# In[37]:

#CLEANS THE DATA
#Writes a clean XML File
def fix_errors(filename, new_file):
    for _, elem in ET.iterparse(filename):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                k = tag.attrib['k']
                v = tag.attrib['v']
                
                #Converts any house number value that is a list to a range
                if k == 'addr:housenumber':
                    if re.search(nums_and_letters,v):
                        continue
                    elif re.search(re.compile(','),v):
                        spl = re.split(',',v)
                        new = str(min(spl)) + '-' + str(max(spl))
                        tag.set('k',k)
                        tag.set('v',new)
                
                #Reduces any postcode that contains more than the accepted 5 digits
                elif k == 'addr:postcode':
                    if re.search(number_only,v):
                        continue
                    else:
                        code = re.search(re.compile('\d{5}'),v).group()
                        tag.set('k',k)
                        tag.set('v',code)
                        
                #Corrects any street name errors
                elif k=='addr:street':
                    if street_error(v):
                        if v.endswith('South'):
                            new = v.rstrip('South').rstrip()
                            tag.set('k',k)
                            tag.set('v',new)
                        else:
                            for i in mapping.keys():
                                if i in v:
                                    new = v.replace(i, mapping[i], 1)
                                    tag.set('k',k)
                                    tag.set('v',new)

                #Removes and tag that does not contain an accepted value
                elif k=='capacity':
                    if re.search(number_only,v):
                        continue
                    else:
                        elem.remove(tag)
                
                #Abbreviates Connecticut
                elif k=='addr:state':
                    if v=='Connecticut':
                        tag.set('k',k)
                        tag.set('v','CT')
                
                #Checks the current format of the fax number and changes it to the accepted format
                elif k=='fax':
                    if re.search(phone_format,v):
                        continue
                    else:
                        first = v[3:6]
                        strip = v[6:].strip()
                        second = strip[0:3]
                        third = strip[3:].strip()
                        new = first + '-' + second + '-' + third
                        tag.set('k',k)
                        tag.set('v',new)
                            
                #Checks the current format of the phone number and changes it to the accepted format
                elif k=='phone':
                    if re.search(phone_format,v):
                        continue
                    else:
                        if re.search(phone_with_paren,v):
                            first = v[(v.find('(')+1):v.find(')')]
                            second = v[(v.find(')')+1):v.find('-')].strip() 
                            third = v[(v.find('-')+1):(v.find('-')+5)].strip()
                            new = first + '-' + second + '-' + third
                            tag.set('k',k)
                            tag.set('v',new)
                        elif re.search(phone_with_plus,v):
                            new = v[3:6] + '-' + v[7:10] + '-' + v[10:]
                            tag.set('k',k)
                            tag.set('v',new)
                        elif re.search(phone_full_10,v):
                            new = v[0:3] + '-' + v[3:6] + '-' + v[6:]
                            tag.set('k',k)
                            tag.set('v',new)
                        elif re.search(phone_with_dots,v):
                            new = v[0:3] + '-' + v[4:7] + '-' + v[8:]
                            tag.set('k',k)
                            tag.set('v',new)
                        else:
                            first = v[3:6]
                            strip = v[6:].strip()
                            second = strip[0:3]
                            third = strip[3:].strip()
                            new = first + '-' + second + '-' + third
                            tag.set('k',k)
                            tag.set('v',new)
                
                #Removes any 'maxspeed' tags that do not match the accpeted format            
                elif k=='maxspeed':
                    if re.search(mph_only,v):
                        continue
                    else:
                        elem.remove(tag)
                
                #Adds 'http://' to and url that does not have it
                elif k=='website':
                    if url_error(v):
                        new = 'http://' + v.strip()
                        tag.set('k',k)
                        tag.set('v',new)
                                
                #Splits any tag that is found to have a population and year for which it is valide
                elif k=='census:population':
                    if re.search(number_only,v):
                        continue
                    elif re.search(re.compile(';\d{4}'),v):
                        pop = v[0:v.find(';')]
                        year = v[v.find(';')+1:]
                        tag.set('k',k)
                        tag.set('v',pop)
                        elem.append(ET.Element('tag', {'k':'source:population','v':str(year)}))
                        elem.remove(tag)
                
                #Converts a deprecated tag
                elif k=='place_name':
                    tag.set('k','name')
                
                #Converts a deprecated tag
                elif k=='wood':
                    tag.set('k', 'leaf_cycle')
                
                #Converts a deprecated tag
                elif k=='drinkable':
                    tag.set('k', 'drinking_water')
                
                #Removes this tag as it is not an acceptable one
                elif k=='Direct mailing':
                    elem.remove(tag)
    
        tree = ET.ElementTree(elem)
        tree.write(new_file)


# In[52]:

fix_errors(data, 'Clean New Haven Data.xml')


# In[54]:

#Checks for errors in the cleaned data
report_data(clean_data)


# In[64]:

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
ADDRESS =[  'addr:city', 'addr:country', 'addr:housename', 'addr:housenumber', 'addr:interpolation', 'addr:postcode', 'addr:state', 'addr:street', 'addr:unit' ]
AMENITY =[ 'amenity', 'backrest', 'bench', 'bicycle_parking', 'capacity', 'dispensing', 'parking', 'socket:tesla_roadster', 'socket:type1', 'atm', 'atm:operator' ]
ANNOTATIONS =[  'description', 'email', 'fax', 'image', 'note_2', 'note:lanes', 'note', 'phone', 'source', 'url', 'website', 'wikipedia', 'colour', 'website:description']
BOUNDARY =[ 'border_type', 'boundary_type', 'boundary', 'admin_level' ]
BUILDING =[ 'building', 'building:levels', 'building:min_level', 'building:part', 'building_1', 'entrance' ]
CYCLEWAY =[ 'cycleway', 'cycleway:left', 'cycleway:right' ]
DIST =[ 'dist:black', 'dist:blue', 'dist:green', 'dist:yellow' ]
FIXME =[  'fixme', 'FIXME', 'FIXME2', 'FIXME3', 'FIXME4', 'FIXME:access', 'complete']
GNIS =[ 'gnis:Class', 'gnis:County', 'gnis:County_num', 'gnis:ST_alpha', 'gnis:ST_num', 'gnis:county_id', 'gnis:county_name', 'gnis:created', 'gnis:feature_id', 'gnis:feature_type', 'gnis:id', 'gnis:import_uuid', 'gnis:reviewed', 'gnis:state_id', 'import_uuid', 'magic:CATEGORY', 'nist:fips_code', 'nist:state_fips' ]
HIGHWAY =[ 'highway', 'footway', 'marker', 'NHS', 'parking:lane:right', 'junction', 'traffic_calming', 'segregated', 'sidewalk', 'traffic_signals:direction', 'lcn', 'traffic_signals:sound', 'lanes', 'lanes:backward', 'lanes:forward' ]
IS_IN =[ 'is_in', 'is_in:continent', 'is_in:country', 'is_in:country_code', 'is_in:iso_3166_2', 'is_in:state', 'is_in:state_code' ]
LANDUSE =[ 'landuse', 'landfill', 'aeroway', 'tourism' ]
LEISURE =[ 'leisure', 'golf', 'par', 'tee' ]
NAME =[ 'name', 'name:de', 'name:en', 'name:ru', 'name_1', 'short_name', 'alt_name', 'loc_name', 'old_name', 'old_name:1970', 'old_name_left', 'old_name_right', 'source:old_name:1970' ]
PAYMENT =[ 'payment:bitcoin', 'payment:cash', 'payment:credit_card' ]
PLACE =[ 'place', 'population' ]
POWER =[ 'power', 'cables', 'generator:method', 'line', 'substation', 'transformer', 'voltage-high', 'voltage' ]
PROPERTIES =[ 'area', 'brand', 'bridge:structure', 'bridge', 'button_operated', 'collection_times', 'covered', 'crossing', 'cutting', 'designation', 'destination', 'disused', 'drive_through', 'ele', 'electrified', 'fee', 'frequency', 'incline', 'inscription', 'internet_access', 'layer', 'level', 'lit', 'location', 'material', 'network', 'opening_hours', 'operator_1', 'operator', 'osmc:symbol', 'ownership', 'smoking', 'start_date', 'supervised', 'surface', 'symbol', 'takeaway', 'tunnel', 'turn:lanes:backward', 'turn:lanes:forward', 'turn:lanes', 'type', 'wheelchair','leaf_cycle' ]
RAILWAY =[ 'railway', 'gauge', 'old_railway_operator', 'passenger', 'from', 'to', 'train', 'usage', 'via' ]
REFERENCE =[ 'ref', 'noref', 'old_ref', 'unsigned_ref', 'lcn_ref', 'destination:ref' ]
RESTRICTIONS =[ 'restriction', 'access', 'bicycle', 'boat', 'foot', 'hgv', 'horse', 'motorcar', 'motor_vehicle', 'vehicle', 'maxheight', 'maxspeed', 'source:maxspeed', 'noexit', 'oneway', 'oneway:bicycle', 'fenced', 'emergency', 'fire_hydrant:type', 'min_age' ]
TIGER =[ 'tiger:cfcc', 'tiger:CLASSFP', 'tiger:county', 'tiger:CPI', 'tiger:FUNCSTAT', 'tiger:LSAD', 'tiger:MTFCC', 'tiger:name_base_1', 'tiger:name_base_2', 'tiger:name_base_3', 'tiger:name_base', 'tiger:name_direction_prefix_1', 'tiger:name_direction_prefix', 'tiger:name_direction_suffix', 'tiger:name_type_1', 'tiger:name_type_2', 'tiger:name_type', 'tiger:NAME', 'tiger:NAMELSAD', 'tiger:PCICBSA', 'tiger:PCINECTA', 'tiger:PLACEFP', 'tiger:PLACENS', 'tiger:PLCIDFP', 'tiger:reviewed', 'tiger:separated', 'tiger:source', 'tiger:STATEFP', 'tiger:tlid', 'tiger:zip_left_1', 'tiger:zip_left_2', 'tiger:zip_left', 'tiger:zip_right_1', 'tiger:zip_right_2', 'tiger:zip_right' ]


# In[38]:

#Shapes the elements of the clean XML File
def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        
        created = {}
        address = {}
        amenity = {}
        annotations = {}
        boundary = {}
        building = {}
        cycleway = {}
        dist = {}
        gnis = {}
        highway = {}
        is_in = {}
        landuse = {}
        leisure = {}
        name = {}
        payment = {}
        place = {}
        power = {}
        properties = {}
        railway = {}
        reference = {}
        restrictions = {}
        tiger = {}
        #fixme = {}
     
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
        sub_keys = []
        
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
                
                elif k in AMENITY:
                    amenity[k]=v
                    
                elif k in ANNOTATIONS:
                    annotations[k]=v
                elif k in BOUNDARY:
                    boundary[k]=v
                elif k in BUILDING:
                    if re.search(re.compile(":"),k):
                        new = k[(k.find(':')+1):]
                        building[new]=v
                    else:
                        building[k]=v
                elif k in CYCLEWAY:
                    if re.search(re.compile(":"),k):
                        new = k[(k.find(':')+1):]
                        cycleway[new]=v
                    else:
                        cycleway[k]=v
                elif k in DIST:
                    new = k[(k.find(':')+1):]
                    dist[new]=v
                
                elif k in GNIS:
                    if re.search(re.compile(":"),k):
                        new = k[(k.find(':')+1):]
                        gnis[new]=v
                    else:
                        gnis[k]=v

                elif k in HIGHWAY:
                    highway[k]=v
                
                elif k in IS_IN:
                    if re.search(re.compile(":"),k):
                        new = k[(k.find(':')+1):]
                        is_in[new]=v
                    else:
                        is_in[k]=v
                elif k in LANDUSE:
                    landuse[k]=v

                elif k in LEISURE:
                    leisure[k]=v

                elif k in NAME:
                    if k.startswith('name:'):
                        new = k[(k.find(':')+1):]
                        name[new]=v
                    else:
                        name[k]=v
                
                elif k in PAYMENT:
                    new = k[(k.find(':')+1):]
                    payment[new]=v

                elif k in PLACE:
                    place[k]=v
                    
                elif k in POWER:
                    power[k]=v

                elif k in PROPERTIES:
                    properties[k]=v
                
                elif k in RAILWAY:
                    railway[k]=v
                    
                elif k in REFERENCE:
                    reference[k]=v

                elif k in RESTRICTIONS:
                    restrictions[k]=v
                
                elif k in TIGER:
                    new = k[(k.find(':')+1):]
                    tiger[new]=v

                elif k in FIXME:
                    continue
                
                else:
                    node[k]=v
            if child.tag == "nd":
                node_refs.append(child.attrib['ref'])
        if node_refs:
            node['node_refs']=node_refs
        if annotations:
            node['annotations']=annotations
        if address:
            node['address']=address
        if amenity:
            node['amenity']=amenity
        if boundary:
            node['boundary']=boundary
        if building:
            node['building']=building
        if cycleway:
            node['cycleway']=cycleway
        if dist:
            node['dist']=dist
        if gnis:
            node['gnis']=gnis
        if highway:
            node['highway']=highway
        if is_in:
            node['is_in']=is_in
        if landuse:
            node['landuse']=landuse
        if leisure:
            node['leisure']=leisure
        if name:
            node['name']=name
        if payment:
            node['payment']=payment
        if place:
            node['place']=place
        if power:
            node['power']=power
        if properties:
            node['properties']=properties
        if railway:
            node['railway']=railway
        if reference:
            node['reference']=reference
        if restrictions:
            node['restrictions']=restrictions
        if tiger:
            node['tiger']=tiger
  
        return node
    else:
        return None


# In[1]:

# Copied from Lesson 6 Excercises
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


# In[11]:

#process_map(clean_data, False)


# In[ ]:



