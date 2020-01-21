# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')


try:
 import xml.etree.cElementTree as ET
except ImportError:
 import xml.etree.ElementTree as ET






def parse():

    tree = ET.ElementTree(file='Projects/test1/Helper/xml/____function_8h.xml')
    root = tree.getroot()


    for elem in tree.iterfind("./compounddef/sectiondef[@kind='func']/memberdef"):
        # for kind in elem.iterfind('//@kind'):
        #     print kind.tag, kind.attrib,kind.text
        print elem.attrib['kind']

        print elem.findall('./definition')[0].text
        print elem.findall('./argsstring')[0].text
        print elem.findall('./name')[0].text


        # print elem.attrib['argsstring']
        # print elem.attrib['name']
