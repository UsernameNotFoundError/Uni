# -*- coding: utf-8 -*-
"""
browse all the gff files and extract the spieces
then collect the files of intrest:
    - gene fasta 
    - gene annotation
    - protein fasta (all and representative)
    - protein features
    - BlastDB
Created on Jun 28  2021

@author: Amine
"""
__version__ = "2.0"
from os import listdir

species_dict = {}
longest_proteins = []
all_the_proteins = []
protein_annotations = []
nucleotide_sequences = []
gene_annotations = []
assembly_list = []
test_gff = []
test_json = []
test_fna = []
test_faa = []

def Species_name_Suprimous(folder_path_list):
    """
    reads in all the files in a folder and extract specific information from 
    the files
    
    Parameters
    ----------
    folder_path : String
        
    Returns
    -------
    Dictionary {Key: , }
    """
    my_dict = {}
    for each_file in folder_path_list:
        with open(each_file, 'r') as my_file:
            for line in my_file.readlines():
                my_list = line.split("|")+ [each_file[:-10]] # Files name will be added referting to spices subgroup
                if 'active' in my_list[-2]:
                    exec("my_dict[\"{assembly_accession}\"] = {species_list}".format(
                        assembly_accession = my_list[2],
                        species_list = my_list))
    
    return my_dict
    


def main():
    species_dict = Species_name_Suprimous(["ArchaeaRefSeq.txt",
                                           "BacteriaRefSeq.txt",
                                           "FungiRefSeq.txt",
                                           "InvertebratesRefSeq.txt",
                                           "MammalianVertebratesRefSeq.txt",
                                           "nonMammalianVertebratesRefSeq.txt",
                                           "PlantsRefSeq.txt"
                                          ])
    print("Ok")
    
    # for i in species_dict:
    #   assembly_list =  
    
    with open('pureged_all_files.txt', 'r') as input_file:
        for line in input_file:
            my_file = line.split('/')
            if "protein.faa" in my_file[-1]:
                if my_file[-2] in species_dict:
                    all_the_proteins.append(line)
                    test_faa.append(my_file[-2])
            elif "protein.rep.fa" in my_file[-1]:
                if my_file[-2] in species_dict:
                    longest_proteins.append(line)
            elif ".json" in my_file[-1]:
                if "GCF_"+my_file[-1]\
                    [ my_file[-1][ my_file[-1].index("@")+1: 
                                  ].index("@")+my_file[-1].index("@")+2:-6]\
                        .replace("_",".") in species_dict:
                    protein_annotations.append(line)
                    test_json.append("GCF_"+my_file[-1]\
                    [ my_file[-1][ my_file[-1].index("@")+1: 
                                  ].index("@")+my_file[-1].index("@")+2:-6]\
                        .replace("_","."))
            elif "genomic.fna" in my_file[-1]:
                if my_file[-2] in species_dict:
                    nucleotide_sequences.append(line)
                    test_fna.append(my_file[-2])
            elif "genomic.gff" in my_file[-1]:
                if my_file[-2] in species_dict:
                    gene_annotations.append(line)
                    test_gff.append(my_file[-2])
            else:
                pass
    return species_dict


if __name__ == "__main__":    
    species_dict = main()
        