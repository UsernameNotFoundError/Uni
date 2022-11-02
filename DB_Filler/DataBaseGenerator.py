__author__ = "Amine"
import wget  # Download files from url
import gzip  # unzif gz files
import shutil
import pandas as pd
from pathlib import Path
import os
from mainapp.models import Assembly, Species
#from mysql.connector import connect
#from Uni import settings
#import sys
#sys.path.insert(0, "path")
#import models


class SuperUpdate():
    """
    This module updates the database

    """
    _version = 0.3
    BASE_DIR = Path(__file__).resolve().parent.parent
    UPDATE_FILES_DIR = os.path.join(BASE_DIR,'updateapp/myupdatefiles')
    def __init__(self):
        print('wow')
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
            search_target_id, search_target_version = row['assembly_accession'].split('.')
            
            #search_target = row['assembly_accession'][4:]
            try:
                thisthing = Assembly.objects.get(assembly_id=search_target_id[4:])
                print('\nHello:\n', index, search_target_id, "go this shit", thisthing)
            except Exception as e:
                print("ERROR:", e)
            try:
                thisthing = Assembly.objects.get(assembly_id=search_target_id[4:], assembly_version=search_target_version)
                print('\nBonjour:\n', index, search_target_id, "go this shit", thisthing)
            except Assembly.DoesNotExist:
                #HERE CODE
                #////////////////////
                # GFF file
                file_name = "genomic.gff.gz"
                file_url = (row['ftp_path']
                                    + '/'
                                    + row['assembly_accession']
                                    + '_'
                                    + row['asm_name']
                                    +"_genomic.gff.gz"
                                    ).replace(" ", "_")

                file_save_loc = os.path.join("/mnt/c/Users/Amine/Documents/GoetheUni/MASTERARBEIT/test/raw_dir",
                                                row['assembly_accession'],
                                                file_name
                                            )
                print("link check:", file_url)
                print("save_loc: ", file_save_loc)
                #os.makedirs(r"/mnt/Users/Amine/Documents/GoetheUni/MASTERARBEIT/test/raw_dir/"+row['assembly_accession'], exist_ok=True)
                #os.system('mkdir /mnt/c/Users/Amine/Documents/GoetheUni/MASTERARBEIT/test/raw_dir/'+row['assembly_accession'])
                wget.download(file_url, file_save_loc)  # Thisdoes not work
                
                with gzip.open(file_save_loc, 'rb') as f_in:
                    with open(file_save_loc[:-3], 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                '''
                self.unzip_gz_file(
                                    file_save_loc,
                                    file_save_loc[:-3]
                                    )
                '''
                print("Done")
                
                #Species
                # FNA file

                # FAA file

                # json file

                # Longest Protein
                # Blast
                #////////////////////
                print("THIS WORKED !!!! ", search_target_version)
            except Exception as e:
                print("ERROR:", e)
            if i==2:
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


    def unzip_gz_file(self,
            source_path,
            save_path=r"C:\Users\Amine\Documents\GoetheUni\MASTERARBEIT\test"):
        """Download and extracts gz files

        Args:
            source_path (string): link to download from
            save_path (string): Where to save the file. Defaults to "C:/Users/Amine/Documents/GoetheUni/MASTERARBEIT/test".
        """
        print("here!!!!! download_gz_file")
        #super_path = "{basepath}/{name}/{file_name}".format()
        #wget.download(source_path, save_path)
        with gzip.open(source_path, 'rb') as f_in:
            with open(save_path, 'wb') as f_out:
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
    #test=SuperUpdate()
