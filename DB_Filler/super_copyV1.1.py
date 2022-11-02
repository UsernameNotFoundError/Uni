# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 2021

@author: Amine
"""

from os import getcwd
from shutil import copy


copy_list = ["/share/gluster/GeneSets/NCBI-Genomes/nonMammalianVertebratesRefSeq/raw_dir/non-mammalianVertebrates-RefSeq_taxid2GCF.txt",
"/share/gluster/GeneSets/NCBI-Genomes/BacteriaRefSeq/raw_dir/BacteriaRefSeq_taxid2GCF.txt",
"/share/gluster/GeneSets/NCBI-Genomes/MammalianVertebratesRefSeq/raw_dir/MammalianVertebratesRefSeq_taxid2GCF.txt",
"/share/gluster/GeneSets/NCBI-Genomes/InvertebratesRefSeq/raw_dir/InvertebratesRefSeq_taxid2GCF.txt",
"/share/gluster/GeneSets/NCBI-Genomes/PlantsRefSeq/raw_dir/PlantsRefSeq_taxid2GCF.txt",
"/share/gluster/GeneSets/NCBI-Genomes/ArchaeaRefSeq/raw_dir/ArchaeaRefSeq_taxid2GCF.txt",
"/share/gluster/GeneSets/NCBI-Genomes/FungiRefSeq/raw_dir/FungiRefSeq_taxid2GCF.txt",
"/share/gluster/GeneSets/NCBI-Genomes/ProtozoaRefSeq/raw_dir/ProtozoaRefSeq_taxid2GCF.txt"]


for i in copy_list:
    copy(i, getcwd() +"/"+ i.split('/')[-1])
    #copy(i, getcwd() +"/"+ i.split('\\')[-1])