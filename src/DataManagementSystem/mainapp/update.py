__author__ = "Amine"
import wget  # Download files from url
import gzip  # unzif gz files
import shutil
import pandas as pd
from pathlib import Path
import os
from mysql.connector import connect
from Uni.settings import DATABASES
#import sys
#sys.path.insert(0, "path")
#import models


class SuperUpdate():
    """
    This module updates the database

    """
    _version = 0.2
    BASE_DIR = Path(__file__).resolve().parent.parent
    UPDATE_FILES_DIR = os.path.join(BASE_DIR,'updateapp/myupdatefiles')
    def __init__(self):
        # 1st Step: get the lastest NCBI
        self.download_refseq()
        self.readdata()
        self.check_database()
        #self.download_gz_file()

    
    def check_database(self):
        """
        check database
        """
        i=-1
        for index, row in self.assembly_df.iterrows():
            i+=1
            search_target = row['assembly_accession'].split('.')[0][4:]

            
            print('\nHello:\n', index, search_target)
            if i==1:
                break
        print(self.assembly_df.head())
    
    def download_refseq(self,
                        refseq_url="https://ftp.ncbi.nlm.nih.gov/genomes/refseq/assembly_summary_refseq.txt",
                        local_path=UPDATE_FILES_DIR
                        ):
        r"""
        Downloads "assembly_summary_refseq.txt" files from Refseq
        Args:
            refseq_url (str, optional): Link to the ftp REFSEQ. Defaults to "https://ftp.ncbi.nlm.nih.gov/genomes/refseq/assembly_summary_refseq.txt".
            local_path (regexp, optional): Saving location. Defaults to "C:\Users\Amine\Documents\GoetheUni\MASTERARBEIT\test".
        """
        #wget.download(refseq_url, local_path)
        self.downloaded_assembly_summary_path = os.path.join(local_path, 'assembly_summary_refseq.txt')
        if Path(self.downloaded_assembly_summary_path).is_file:
            print("Assembly downloaded successfully!")
        else:
            print("Assembly downloaded failed!")
            raise ("Could not download file.")


    def download_gz_file(self,
            refseq_url="https://ftp.ncbi.nlm.nih.gov/genomes/refseq/assembly_summary_refseq.txt",
            local_path=r"C:\Users\Amine\Documents\GoetheUni\MASTERARBEIT\test"):
        super_path = "{basepath/{name}/{file_name}".format()
        with gzip.open(r"C:\Users\Amine\Documents\GoetheUni\MASTERARBEIT\test\GCF_000001405.40_GRCh38.p14_protein.faa.gz", 'rb') as f_in:
            with open(r"C:\Users\Amine\Documents\GoetheUni\MASTERARBEIT\test\human_protein.faa", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)


    def readdata(self):
        """
        Reads "assembly_summary_refseq.txt" filters out non needed data
        _______________
        Input:  self.assembly_df -> PandaDataFrame
                self.downloaded_assembly_summary_path -> string
        _______________
        output: self.assembly_df
        _______________
        Returns: None
        """        
        self.assembly_df = pd.read_csv(
                                    self.downloaded_assembly_summary_path,
                                    delimiter="\t",
                                    skiprows=1,
                                    dtype='unicode'
                                    )
        # ____ Remove not needed collumns !! ______
        # Kept Collumns: # assembly_accession, refseq_category, taxid,
        # organism_name, asm_name, ftp_path
        self.assembly_df.drop(
                ['bioproject', 'biosample', 'wgs_master', 'species_taxid',
                'species_taxid', 'species_taxid', 'infraspecific_name',
                'isolate', 'version_status', 'assembly_level', 'release_type',
                'genome_rep', 'seq_rel_date', 'submitter', 'gbrs_paired_asm',
                'paired_asm_comp', 'excluded_from_refseq',
                'relation_to_type_material', 'asm_not_live_date',
                ],
                inplace=True,
                axis=1
                )
        self.assembly_df.rename(columns={ self.assembly_df.columns[0]: "assembly_accession" }, inplace = True)


if __name__=="__main__":
    print("What are you doing?")
    test=SuperUpdate()
