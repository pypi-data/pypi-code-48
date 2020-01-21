#!/usr/bin/python
# -*- coding: UTF-8 -*-


#提取字符串，以2个key
def PickupFor2Key(str,key1,key2):
    fx = str.find(key1)
    if fx >= 0:
        fy = str.find(key2,fx)
    else:
        return (str,-1)

    if fy < fx:
        return str
    if fx < 0 or fy < 0:
        return (str,-1)

    val = str[fx+len(key1):fy]
    return (val,1)

#拼接字符串，以2个key
def RemoveFor2Key(str,key1,key2):
    fx = str.find(key1)
    if fx >= 0:
        fy = str.find(key2,fx)
    else:
        return (str, -1)

    if fy < fx:
        return (str, -1)
    if fx < 0 or fy < 0:
        return (str, -1)


    fs = str[:fx-1]
    fe = str[fy+len(key2):]

    val = fs + fe
    return (val,1)

def find_lastpos(string, str):
    last_position = -1
    while True:
        position = string.find(str, last_position + 1)
        if position == -1:
            return last_position
        last_position = position