__author__ = 'wintere', 'wchen'

import sys,os
from lxml import etree
import codecs
import re
import traceback
import conversion_dict as cd
import argparse
reserved_char = dict()

# XML reserved chars: to be stripped except for 'and'
# &gt;
reserved_char['>'] = '@'
# &lt;
reserved_char['<'] = '@'
# &amp;
reserved_char['&'] = 'and'
# &#37;
reserved_char['%'] = '@'

conversion_dict = cd.getConversionDict()

def strip_html(data):
    """
    Use regular expression to remove the html tags

    Return:  string without html tags
    """
    p = re.compile(r'<.*?>', re.DOTALL)
    return p.sub('', data)

def strip_htmlcomment(data):
    """
    Use regular expression to remove the html comments

    Return:  string without html comments
    """
    p = re.compile(r'<!--.*?-->', re.DOTALL)
    return p.sub('', data)

# process for <SEG>, <GAP>, and html comments
def special_tag_process(filepath):
    seg_tag_reg = re.compile(r'<SEG.*?>.*?</SEG>')
    gap_tag_reg = re.compile(r'<GAP.*?/>')
    sup_tag_reg = re.compile(r'<SUP.*?>.*?</SUP>')
    sub_tag_reg = re.compile(r'<SUB.*?>.*?</SUB>')
    html_reg = re.compile(r'&amp;')
    file_str = ''
    with open(filepath, mode="r", encoding='utf-8') as fr:
        file_str = fr.read()
        seg_toks = seg_tag_reg.findall(file_str)
        gap_toks = gap_tag_reg.findall(file_str)
        sup_toks = sup_tag_reg.findall(file_str)
        sub_toks = sub_tag_reg.findall(file_str)
        html_toks = html_reg.findall(file_str)
        for tok in seg_toks:
            new_tok = strip_html(tok)
            file_str = file_str.replace(tok, new_tok)
        for tok in gap_toks:
            if "duplicate" in tok:
                file_str = file_str.replace(tok,'@') #strip out duplicate markers
            elif "word" in tok or "foreign" in tok or "page" in tok:
                file_str = file_str.replace(tok,'(...)')
            else:
                file_str = file_str.replace(tok,'^')
        for tok in sup_toks:
            char = re.sub('<SUP>|</SUP>', '', tok)
            file_str = file_str.replace(tok,char)
        for tok in sub_toks:
            char = re.sub('<SUB>|</SUB>','', tok)
            file_str = file_str.replace(tok,char)
        for tok in html_toks:
            file_str = file_str.replace(tok, '')
    fr.close()
    file_str = strip_htmlcomment(file_str)
    return codecs.encode(file_str, encoding='utf-8', errors='ignore')

def clean_word(string):
    for char in string:
        try:
            codecs.encode(char, 'ascii', errors='strict')
        except UnicodeEncodeError:
            if char in conversion_dict:
                string = string.replace(char, conversion_dict[char])
            else:
                string = string.replace(char, '@')
    string = string.replace('|', '')
    return string

#removes all unicode characters from a utf-8 xml file
def simple_clean(filepath, strip=False):
    parser = etree.XMLParser(remove_blank_text=True)

    #returns byte string of file
    file_bytes = special_tag_process(filepath)
    try:
        root = etree.fromstring(file_bytes, parser)
    # Deal with any special cases that break the XML parser
    except etree.XMLSyntaxError as e:
        return 0

    for node in root.iter():
        # remove unicode characters from asterisks
        if node.text is not None:
            text = node.text
            for key in reserved_char.keys():
                if key in text.split():
                    text = text.replace(key, reserved_char[key])
            node.text = clean_word(text)
        if node.tail is not None:
            tail = node.tail.replace('&amp;', 'and')
            for key in reserved_char.keys():
                if key in tail.split():
                    tail = tail.replace(key, reserved_char[key])
            node.tail = clean_word(tail)
        #scrub unicode characters from attributes
        if node.attrib is not None:
            for key, val in node.attrib.items():
                node.attrib[key] = clean_word(val)

    xml_string = etree.tostring(root, method='xml', pretty_print=True, encoding='ascii')
    if strip:
        xml_string = xml_string.replace('@', '')
    try:
        #tests that string can be converted back into an xml tree
        etree.fromstring(xml_string, parser)
        return xml_string.decode('ascii')
    except:
        traceback.print_exc(file=sys.stdout)
        return 1

#a cleaning method for plain text files
def txt_clean(filepath):
    f = open(filepath, mode='r', encoding='utf-8', errors='ignore')
    file_str = f.readlines()
    s = ''
    for line in file_str:
        lc = clean_word(line)
        s += lc
    s = strip_html(s)
    s = strip_htmlcomment(s)
    return s



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='VEP Character Cleaner')
    parser.add_argument('input_path', help='path to corpus to character clean relative to the location of this script')
    parser.add_argument('output_path', help='path to output folder relative to the location of this script')
    parser.add_argument('--strip_unknown', help='strips unknown unicode characters, if disabled unknown unicode characters will be marked with @', action='store_true')

    args = parser.parse_args()
    srcdir = args.input_path
    destdir = args.output_path
    strip = args.strip_unknown

    if not os.path.exists(destdir):
        os.makedirs(destdir)

    if not os.path.exists(srcdir):
        print("Error: Input path", srcdir,"does not exist.")
        exit()
    if os.path.isdir(srcdir):
        failedFiles = [] #retain a list of unparseable files for batch processing
        for dirpath, subdirs, files in os.walk(srcdir):
            for file in files:
                if file.endswith(".xml") or file.endswith(".txt"): # only processing XML and TXT files
                    filePath = os.path.join(dirpath, file)
                    op_path = os.path.join(destdir, file)
                    print('generating... '+ op_path)
                    if file.endswith(".xml"):
                        outputStr = simple_clean(filePath)
                    else:
                        outputStr = txt_clean(filePath)
                    if outputStr == 0 or outputStr == 1: #check for error codes
                        failedFiles.append(filePath)
                        continue
                    outputFile = open(op_path, mode='w', encoding='ascii')
                    outputFile.write(outputStr)
                    outputFile.close()
                else:
                    print("skipping file", file, "because it is not an .xml or .txt file")
        if len(failedFiles) > 0:
            print("\nBatch completed with errors. Unable to parse the following files: ")
            for filename in failedFiles:
                print(filename)
        else:
            print("\nBatch completed successfully.")
    #if source exists but isn't a directory, it must be a file
    else:
        filePath = srcdir
        if filePath.endswith(".xml"):
            outputStr = simple_clean(filePath)
        elif filePath.endswith(".txt"):
            outputStr = txt_clean(filePath)
        else:
            print("Error: invalid input file.", filePath,"is not an .xml or .txt file.")
            exit()
        fn = os.path.basename(filePath)
        outputPath = os.path.join(destdir, fn)
        outputFile = open(outputPath, mode='w', encoding='ascii')
        print('generating... '+ outputPath)
        outputFile.write(outputStr)
        outputFile.close()

