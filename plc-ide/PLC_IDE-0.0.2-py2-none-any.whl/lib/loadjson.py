#!/usr/bin/python
import json

data = '{"a" : 1,"b" : 2, "c" : 3, "d" : 4,"e" : 5 }';

json1 = json.loads(data)

print json1["c"]

keys = json1.keys()

print "-------------------"

for aj_key in json1.keys():
    print aj_key

print "-------------------"

print json1