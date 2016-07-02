
# coding: utf-8

# In[1]:

get_ipython().magic(u'matplotlib inline')
from pymongo import MongoClient
import pprint
import matplotlib.pyplot as plt
import numpy as np


# In[2]:

client = MongoClient('mongodb://localhost:27017/')


# In[3]:

db = client.udacity


# In[56]:

#Count how many restaurants are tagged with 'pizza'
def find_pizza():
    count = 0
    pizza = db.new_haven.find({"cuisine" : "pizza"})
    for a in pizza:
        #pprint.pprint(a)
        count+=1
    print count


# In[57]:

find_pizza()


# In[58]:

#Count how many restaurants are tagged with 'italian'
def find_italian():
    count = 0
    italian = db.new_haven.find({"cuisine" : "italian"})
    for a in italian:
        #pprint.pprint(a)
        count+=1
    print count


# In[59]:

find_italian()


# In[60]:

#Count how many restaurants are tagged with 'chinese'
def find_chinese():
    count = 0
    pizza = db.new_haven.find({"cuisine" : "chinese"})
    for a in pizza:
        #pprint.pprint(a)
        count+=1
    print count


# In[61]:

find_chinese()


# In[8]:

def find_church():
    count = 0
    church = db.new_haven.find({"religion" : {"$exists":1}})
    for a in church:
        #pprint.pprint(a)
        count+=1
    print count


# In[9]:

find_church()


# In[67]:

#Count the total number of entries in the dataset
db.new_haven.find().count()


# In[68]:

#Count the number of 'Nodes' in the dataset
db.new_haven.find({"type":"node"}).count()


# In[69]:

#Count the number of 'Ways in the dataset
db.new_haven.find({"type":"way"}).count()


# In[70]:

#Count the number of contributors to the entries in the dataset
users = db.new_haven.distinct("created.user").__len__()
print users


# In[71]:

#Find the contributor who has created or edited the most entries in the dataset
def top_contribute():
    pipeline = [{"$project":{"_id":"$_id", "contributor":"$created.user"}}, {"$group" : {"_id": "$contributor", "count":{"$sum":1}}},{"$sort" : {"count" : -1}},{"$limit" : 1}]
    for i in db.new_haven.aggregate(pipeline):
        print i


# In[72]:

top_contribute()


# In[73]:

#Count the number of contributors with only one entry
def one_contribution():
    users = []
    pipeline = [{"$project":{"_id":"$_id", "contributor":"$created.user"}}, {"$group" : {"_id": "$contributor", "count":{"$sum":1}}},{"$match":{"count":{"$lt":2}}}]
    for i in db.new_haven.aggregate(pipeline):
        users.append(i)
    print len(users)


# In[74]:

one_contribution()


# In[75]:

#Count the number of entries tagged with the given amenity
def find_amenity(amenity):
    count = 0
    found = db.new_haven.find({"amenity.amenity" : amenity})
    for a in found:
        #pprint.pprint(a)
        count+=1
    print count


# In[76]:

find_amenity('place_of_worship')


# In[79]:

#Determine how many entries were generated or last edited per calendar year
def entries_per_year():
    times = {}
    pipeline = [{"$project":{"_id":"$_id", "timestamp":"$created.timestamp"}}]
    for i in db.new_haven.aggregate(pipeline):
        if i['timestamp'][:4] in times.keys():
            times[i['timestamp'][:4]]=times[i['timestamp'][:4]]+1
        else:
            times[i['timestamp'][:4]]=1
    print times


# In[80]:

entries_per_year()


# In[29]:

#Number of entries per year, sorted
x = []
y = []
pipeline = [{"$project":{"_id":"$_id", "year":{"$substr": ["$created.timestamp",0,4]}}},{"$group" : {"_id": "$year", "count":{"$sum":1}}}, {"$sort" : {"count" : -1}}, {"$project": {"number_of_entries":"$count"}}]
for i in db.new_haven.aggregate(pipeline):
    print i
    x.append(int(i['_id']))
    y.append(i['number_of_entries'])




# In[81]:

#Display each type of cuisine in the dataset sorted by number of entries and percentage of total 'cuisine' entries
cuisines = []
for i in db.new_haven.find({"cuisine" : {"$exists":1}}):
    cuisines.append(i['cuisine'])
print "Total Number of Restaurants with Cuisine Tag: " + str(len(cuisines))
pipeline = [{"$match":{"cuisine":{"$exists":1}}},{"$group":{"_id":"$cuisine", "count":{"$sum":1}}}, {"$project":{"_id":"$_id", "count":"$count", "percentage":{"$multiply" : [{"$divide":["$count",len(cuisines)]},100]}}}, {"$sort":{"count":-1}}]
for i in db.new_haven.aggregate(pipeline):
    print i


# In[83]:

#Tallies the number of entries for which 'Yale' is in the 'name' or 'operator' tag values
name_pipeline = [{"$match" : {"name.name":{"$exists":1}}}, {"$project" : {"_id" : "$_id", "name" : "$name.name"}}]
name = db.new_haven.aggregate(name_pipeline)
operator_pipeline = [{"$match" : {"properties.operator":{"$exists":1}}}, {"$project" : {"_id" : "$_id", "operator" : "$properties.operator"}}]
operator = db.new_haven.aggregate(operator_pipeline)
yale_docs = set([])
for a in name:
    if a['name'].find('Yale') > -1:
        yale_docs.add(a["_id"])
for b in operator:
    if b['operator'].find('Yale') > -1:
        yale_docs.add(b['_id'])   
print len(yale_docs)    


# In[86]:

#A sorted count of the number of building per zip code
zips_pipeline = [{"$match" : {"building.building":{"$exists":1}}}, {"$match" : {"address.postcode":{"$exists":1}}}, {"$group" : {"_id" : "$address.postcode", "count" : {"$sum" : 1}}}, {"$sort":{"count":-1}}]
zips = db.new_haven.aggregate(zips_pipeline)
for a in zips:
    pprint.pprint(a)


# In[87]:

#Total number of entries with the 'building' tag
buildings = [{"$match" : {"building.building":{"$exists":1}}}]
count = 0
for a in db.new_haven.aggregate(buildings):
    count+=1
print count


# In[54]:

def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print "%s: %d" % (k,v)


# In[88]:

#Finds the streets in the dataset that span the highest number of postcodes
road_zips = {}
road_zip_pipeline = [{"$match":{"tiger":{"$exists":1}}}, {"$match":{"highway":{"$exists":1}}},{"$match":{"name.name":{"$exists":1}}}, {"$project": {"_id":"$name.name", "zip_1":"$tiger.zip_left", "zip_2":"$tiger.zip_left_1","zip_3":"$tiger.zip_left_2","zip_4":"$tiger.zip_right","zip_5":"$tiger.zip_right_1","zip_6":"$tiger.zip_right_2"}}]
for i in db.new_haven.aggregate(road_zip_pipeline):
    if len(i)>1:
        temp_list=[]
        name = 0
        for a in i.values():
            if a.startswith('0'):
                temp_list.append(a)
            else:
                name=a
        if name in road_zips.keys():
            for b in temp_list:
                road_zips[name].add(b)
        else:
            road_zips[name]=set()
            for b in temp_list:
                road_zips[name].add(b)
sort_dict = {}
for j in road_zips:
    sort_dict[j]=len(road_zips[j])
for k in sorted(sort_dict.items(), key=lambda x:x[1]):
    if k[1]>2:
        print k[0] + ' : ' + str(k[1]) 
        print road_zips[k[0]]

