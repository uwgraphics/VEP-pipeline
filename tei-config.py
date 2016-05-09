# -*- coding: utf-8 -*-
__author__ = 'wchen'

import lxml
from lxml import etree
import sys
import os
import re

import yaml # used to generating the description file

if len(sys.argv) < 2:
    print("usage: {0} [XML_PATH] [-t [config_type]]".format(__file__))
    print("options:")
    print("\t-t\t[config_type]: 1)'plaintext'(default) 2)'specialtag' 3)'withheader'")
    sys.exit(0)

rootdir = sys.argv[1]

config_type = 'plaintext'
if len(sys.argv) > 2:
    if sys.argv[2] == '-t':
        config_type = sys.argv[3]

distinct_tag_path = set()
distinct_tag = set()
attrib_dict = {}
root_tag = set()
file_num = 0
for dirpath, subdirs, files in os.walk(rootdir):
    for file in files:
        if file.endswith(".xml"): # only processing XML files
            filePath = os.path.join(dirpath, file)
            #print filePath
            file_num += 1
            tree = etree.parse(filePath)
            treeroot = tree.getroot()
            for child in treeroot.iter():
                # fields for child: child.tag, child.attrib, child.text,child.tail
                if child is treeroot:
                    root_tag.add(child.tag)

                if type(child.tag) is str:
                    distinct_tag.add(child.tag) 
                    for att in child.attrib:
                        try:
                            attrib_dict[child.tag].add(att)
                        except KeyError: # if it's the first time meeting the child.tag
                            attrib_dict[child.tag] = set()
                            attrib_dict[child.tag].add(att) 
                else:
                    pass
                try:
                    s = str(tree.getelementpath(child))
                    # process the duplicate cases like "EEBO/TEXT/BODY/DIV1[3]/DIV2[6]/P[20]/HI[5]"
                    # the regexp will remove the [] part -> "EEBO/TEXT/BODY/DIV1/DIV2/P/HI"
                    distinct_tag_path.add(re.sub(r'(\[(\d)+\])', '', s))
                except ValueError:
                    pass



#print attrib_dict
f = open('config.yaml', 'w')

special_tag = ["SUB","SUP","VEP-CC","normalised"]
newLine_tag = ["L","HEAD"]
double_newLine = ["P"]
header_tag = ["TEMPHEAD","EVDESCR","CHANGE","RESPSTMT","NAME","RESP","EEBO","IDG","STC","BIBNO","VID",
"TITLE","AUTHOR","PUBLISHER","PUBPLACE"]
ignored_tag = []

body_tag = set()

eebo = treeroot.find("EEBO")

for child in eebo.iter():
    if child.tag not in header_tag:
        body_tag.add(child.tag)

for s in distinct_tag:
    if config_type == 'plaintext':
        f.write( s + ":\n")
        f.write("   " + "main-config" +":\n")
        s = str.upper(s)
        if s in root_tag:
            pass
        elif s in header_tag:
            f.write("      - csv\n")
        elif s in special_tag: 
            f.write("      - text\n")
        elif s in body_tag:
            f.write("      - text\n")
        if s in newLine_tag:
            f.write("      - newLine\n")
        elif s in double_newLine:
            f.write("      - doubleNewLine\n")
        try:
            for att in attrib_dict[s]:
                f.write("   " + att +":\n")
                if s in header_tag:
                    f.write("      " + "- csv\n")
        except KeyError: # if the tag has no attrib
            pass;

    elif config_type == 'specialtag':
        f.write( s + ":\n")
        f.write("   " + "main-config" +":\n")
        if s in root_tag:
            pass
        elif s in header_tag:
            f.write("      - csv\n")
        elif s in special_tag: 
            f.write("      - tag\n")
            f.write("      - text\n")
        elif s in body_tag:
            f.write("      - text\n")
        if s in newLine_tag:
            f.write("      - newLine\n")
        elif s in double_newLine:
            f.write("      - doubleNewLine\n")
        try:
            for att in attrib_dict[s]:
                f.write("   " + att +":\n")
                if s in header_tag:
                    f.write("      " + "- csv\n")
        except KeyError: # if the tag has no attrib
            pass
    elif config_type == 'withheader':
        f.write( s + ":\n")
        f.write("   " + "main-config" +":\n")
        if s in root_tag:
            pass
        elif s in header_tag:
            f.write("      - tag\n")
            f.write("      - text\n")
        elif s in special_tag: 
            f.write("      - tag\n")
            f.write("      - text\n")
        elif s in body_tag:
            f.write("      - text\n")
        if s in newLine_tag:
            f.write("      - newLine\n")
        elif s in double_newLine:
            f.write("      - doubleNewLine\n")
        try:
            for att in attrib_dict[s]:
                f.write("   " + att +":\n")
                if s in header_tag:
                    f.write("      " + "- csv\n")
        except KeyError: # if the tag has no attrib
            pass;
    f.write("\n")

f.close()

"""
for s in distinct_tag_path:
    print s
"""
print("{0} files are processed\n".format(file_num))
print("#distinct_tag: ", len(distinct_tag), "; #distinct_tag_path: ", len(distinct_tag_path))
print("the generated config file: config.yaml")

