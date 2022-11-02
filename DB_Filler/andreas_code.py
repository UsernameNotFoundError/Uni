# -*- coding: utf-8 -*-
"""
Created on Thu Oct 28 14:10:49 2021

@author: Amine
"""

from Bio import Entrez
import xml.etree.ElementTree as ET

taxid = 9606
handle = Entrez.efetch(db="taxonomy", id=taxid, retmode='xml')
raw_data = handle.read().decode()
root = ET.fromstring(raw_data)
handle.close()

for taxon in root:
    for child in taxon:
        if child.tag == 'Lineage':
            linstring = child.text