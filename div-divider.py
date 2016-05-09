# -*- coding: utf-8 -*-

import lxml
from lxml import etree
import sys
import os
import re
import csv
import codecs

def csv_output(filename, div_type_dict, header_dict, specified_type):
    csvfile = codecs.open(filename, mode='w', encoding='utf-8')
    columns = ['FileName(IDG)', 'Type', 'Counts', 'Title', 'Author', 'Publication Date', 'Filing Date']
    csvwriter = csv.DictWriter(csvfile, fieldnames=columns)
    csvwriter.writeheader()
    for idg in div_type_dict.keys():
        row = {}
        row['FileName(IDG)'] = idg
        for div_type in div_type_dict[idg].keys():
            if (specified_type is not None and div_type in specified_type) or specified_type is None:
                row['Type'] = div_type
                row['Counts'] = str(div_type_dict[idg][div_type])
                row['Title'] = (header_dict[idg]['TITLE']).encode('ascii','ignore')
                row['Author'] = (header_dict[idg]['AUTHOR']).encode('ascii','ignore')
                row['Publication Date'] = (header_dict[idg]['PDATE']).encode('ascii','ignore')
                row['Filing Date'] = (header_dict[idg]['FDATE']).encode('ascii','ignore')
                csvwriter.writerow(row)
    csvfile.close()

def header_build(dom_root): 
    header_dict = dict()
    author = dom_root.find('.//AUTHOR') # find AUTHOR element anywhere in the tree
    title = dom_root.find('.//TITLE')
    date = dom_root.findall('.//DATE')
    if author is not None:
        header_dict['AUTHOR'] = author.text
    else: 
        header_dict['AUTHOR'] = ''
    if title is not None:
        header_dict['TITLE'] = title.text
    else:
        header_dict['TITLE'] = ''
    if date is not None and len(date) > 0:
        header_dict['FDATE'] = date[0].text
    else:
        header_dict['FDATE'] = ''
    if date is not None and len(date) > 1:
        header_dict['PDATE'] = date[1].text
    else:
        header_dict['PDATE'] = ''
    return header_dict
    

def div_divide(filepath, specified_type, dest_dir):
    tree = etree.parse(filepath)
    treeroot = tree.getroot()
    print(dest_dir)
    types_dict = dict()

    div1_id = 0
    for child in treeroot.iter():
        if re.match(r'DIV[\d]+', str(child.tag)) is not None:
            xmlpath = str(tree.getelementpath(child))
            distinct_xmlpath = re.sub(r'(\[(\d)+\])', '', xmlpath)
            div_counts = distinct_xmlpath.count('DIV')
            typename = child.attrib['TYPE']
            typename = str.replace(typename,' ', '_')
            typename = str.replace(typename, '/', '_')
            if (div_counts > 1) and (specified_type is not None) and (typename not in specified_type):
                continue
            if typename not in types_dict.keys():
                types_dict[typename] = 0
            div1_id += 1
            types_dict[typename] += 1
            if (specified_type is not None and typename in specified_type) or (specified_type is None):
                xml_string = etree.tostring(child, method='xml', pretty_print=True, encoding='utf-8')
                #print xml_string
                output_file_without_ext = os.path.relpath(os.path.splitext(filepath)[0])
                output_file = os.path.join(dest_dir,os.path.basename(output_file_without_ext) + "{0:03d}".format(div1_id) + '_'+typename+'_'+"{0:03d}".format(types_dict[typename]))
                if div_counts > 1:
                    output_file += '_L'+"{0:01d}".format(div_counts)
                output_file += '.xml'
                print(output_file)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                fw = open(output_file, 'wb')
                fw.write(xml_string)
                fw.close()
    return types_dict

if __name__ == '__main__':
    options = ['-t', '-o']
    if len(sys.argv) < 2:
        print("usage: "+__file__+" src_path(dir/file) [dest_dir] [-options]")
        print("\toptions:\n\t\t-t type1 [type2]...\n\t\t-o csvfile")
        sys.exit(0)
    if len(sys.argv) > 2:  
        dest_dir = sys.argv[2]
    else:
        dest_dir = '.'
    specified_type = None
    csv_outfile = None
    if len(sys.argv) >= 5:
        if sys.argv[3] not in options:
            print("option: " + sys.argv[3] + " is not recognized.")
            sys.exit(0)
        if '-t' in sys.argv:
            type_index = sys.argv.index('-t')
            while type_index+1 < len(sys.argv):
                if sys.argv[type_index+1] == '-o':
                    break
                specified_type.append(str(sys.argv[type_index+1]))
                type_index += 1
        if '-o' in sys.argv:
            out_index = sys.argv.index('-o')
            csv_outfile = str(sys.argv[out_index+1])

    csv_div_dict = dict() 
    csv_header_dict = dict() 
    
    srcPath = sys.argv[1]
    if os.path.isfile(srcPath):
        tcp_filename = srcPath.split('/')[-1].replace('.headed', '').replace('.xml','')
        csv_div_dict[tcp_filename] = div_divide(srcPath, specified_type, dest_dir)
        csv_header_dict[tcp_filename] = header_build(etree.parse(srcPath).getroot())
        #div_divide(srcPath, specified_type)
    elif os.path.isdir(srcPath): 
        for dirpath, subdirs, files in os.walk(srcPath):
            for file in files:
                if file.endswith(".xml"): # only processing XML files
                    filePath = os.path.join(dirpath, file)
                    base = os.path.split(filePath)[1]
                    print(base)
                    tcp_filename = ''
                    print(tcp_filename)
                    csv_div_dict[tcp_filename] = div_divide(filePath, specified_type, dest_dir) 
                    csv_header_dict[tcp_filename] = header_build(etree.parse(filePath).getroot())
    
    # output csv list if '-o' option is enabled
    if csv_outfile is not None:
        csv_output(csv_outfile, csv_div_dict, csv_header_dict, specified_type)
