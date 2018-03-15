import os, os.path, sys
import glob
from xml.etree import ElementTree as ET
import pdb
import OrderedDict

operator_list = ['read', 'apply_orbit_file', 'thermal_noise_removal', 'calibration', 'topsar_deburst', 'subset', 'write']
operator_dict = {'read':{'infile':'filename'}, 'apply_orit_file':{'refid':'read'},'thermal_noise_removal':{}, 'calibration':{}, 'topsar_deburst':{}, 'subset':{}, 'write':{}}

path = '/media/tweiss/Work/GitHub/multiply-org/sar-pre-processing/xml_files/operators'

for i, operator_name in enumerate(operator_list):
    if i == 0:
        tree = ET.parse(os.path.join(path,operator_name+'.xml'))
        root = tree.getroot()
        for elem in root.getiterator():
            try:
                elem.text = elem.text.replace('$id', operator_name+str(i))
                refid = operator_name+str(i)
            except AttributeError:
                pass
    else:
        document = ET.parse(os.path.join(path,operator_name+'.xml'))
        for elem in root.getiterator():
            try:
                elem.text = elem.text.replace('$id', operator_name+str(i))
                elem.text = elem.text.replace('$refid', refid)
            except AttributeError:
                pass

        childNodeList = document.findall('node')

        for node in childNodeList:
            root.append(node)

tree.write('/media/tweiss/Work/GitHub/multiply-org/sar-pre-processing/xml_files/operators/read_write2.xml')


# tempFile = '/media/tweiss/Work/GitHub/multiply-org/sar-pre-processing/xml_files/operators/read_write.xml'
# xpathQuery = 'node'

# tree = ET.parse('/media/tweiss/Work/GitHub/multiply-org/sar-pre-processing/xml_files/operators/read_write.xml')

# root = tree.getroot()
# document = ET.parse(tempFile)

# childNodeList = document.findall(xpathQuery)

# for node in childNodeList:
#     root.append(node)



# tree.write('/media/tweiss/Work/GitHub/multiply-org/sar-pre-processing/xml_files/operators/read_write2.xml')

