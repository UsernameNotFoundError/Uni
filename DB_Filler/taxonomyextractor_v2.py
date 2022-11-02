# -*- coding: utf-8 -*-
"""
Created on Thu Oct 28 14:10:49 2021

@author: Amine
"""
from os.path import join
from os import listdir
from pathlib import Path
from Bio import Entrez
import xml.etree.ElementTree as ET

#______________________________________________________________
Entrez.email = "xagedac687@dukeoo.com"  # Change E-mail here ###
#______________________________________________________________

class taxonoystringer:
    """Extract taxxonomy string from ncbi and saves it in a file)"""
    def __init__(self):
        print("started")
        
        self.spiecies_extractorV2_modified()
        self.tax_string_extractor_modified()
        
        print("end")
        
    
    def spiecies_extractorV2_modified(self, my_location = "AdditionalData"):
        """
        Checks  all the files in a specific location and 
        importes:
            from os.path import join
            from os import listdir
            from pathlib import Path
        Parameters
        ----------
        my_location : String
            Path to the folder
            
        Returns
        -------
        None 
        (but ceates a dictionary : self.species_data_dict
         and a list: self.files_list)
            
        """
        self.files_list = [join(my_location, f) \
                            for f in listdir(my_location) 
                            ]
        self.species_data_dict = {}
        self.done_species_data_set = set() #if the file exists
        for each_file in self.files_list:
            file_name = each_file.split("\\")[-1]
            with open(each_file, 'r') as self.input_file:
                for line in self.input_file:
                    my_list = line.split("|")+ [file_name[:-10]] # Files name will be added referting to spices subgroup
                    if 'active' in my_list[-2]:
                        exec("self.species_data_dict[\"{assembly_accession}\"] = {species_list}".format(
                        assembly_accession = my_list[2],
                        species_list = my_list))
        
        my_file = Path("all_taxa_string.txt")
        if my_file.is_file():
            with open(my_file, "r") as filled_file:
                for line in filled_file:
                    self.done_species_data_set.add(line.split(";")[-3])
                    
                    
        

    def tax_string_extractor_modified(self):
        """  
        requires  species_data_dict to be filled
        imports: 
            from Bio import Entrez
            import xml.etree.ElementTree as ET
        """
        with open("all_taxa_string.txt", 'a') as save_file:
            for my_values in self.species_data_dict.values():
                if my_values[-4] in self.done_species_data_set:
                    continue
                
                taxid = my_values[0]
                handle = Entrez.efetch(db="taxonomy", id=taxid, retmode='xml')
                raw_data = handle.read().decode()
                root = ET.fromstring(raw_data)
                handle.close()
                
                for taxon in root:
                    for child in taxon:
                        if child.tag == 'Lineage':
                            linstring = child.text
                            save_file.write(linstring+";"+";".join(my_values[:-1]))
                            
        
            
my_instance = taxonoystringer()