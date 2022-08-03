__author__ = "Amine"
from datetime import date
from unicodedata import name
import wget  # Download files from url
import gzip  # unzif gz files
import shutil
import pandas as pd
from pathlib import Path
import os
from mainapp.models import Assembly, Species, Genomicannotation, Proteinset
from mysql.connector import connect  # in case model doe not work
from Uni.settings import DATABASES
from Bio import Entrez
import xml.etree.ElementTree as ET


class SuperUpdate():
    """
    This module updates the database

    """
    _version = 1.0
    BASE_DIR = Path(__file__).resolve().parent.parent
    UPDATE_FILES_DIR = os.path.join(BASE_DIR,'updateapp/myupdatefiles')
    UPDATE_LOCATION = "/mnt/c/Users/Amine/Documents/GoetheUni/MASTERARBEIT/test/" # Change me

    def __init__(self, ignore_this_taxa="" , do_only_this_taxa="") -> None:
        print("START THREAD")
        self.updating_status = 0
        self._stop_me = False
        self.html_print = ""
        self.ignore_this_taxa = ignore_this_taxa
        self.do_only_this_taxa = do_only_this_taxa
        self._job_done = False


    def _start_update(self):
        """
        Called with an other thread to ensure simultaneous execution 
        """
        print('Initiating update!')
        # 1st Step: get the lastest NCBI assembly summary
        self.download_refseq()
        # 2nd Step: Filter unnecassary data
        self.readdata()
        # 3rd Check data base add and download lastest
        self.check_database()
        self._stop_me = True
        self._job_done = True

    
    def check_database(self):
        """
        check database and download the nessassary data needed and umpdate mySQL database
        ___________
        imports:
            wget
            gzip
            mysql.connector.connect
        """
        self._write_log("Comparing Database data with the new one...\n")
        for index, row in self.assembly_df.iterrows():
            if index%500 == 0:
                self.updating_status = self._get_update_progress(index)
            if self._stop_me:
                break
            self._job_done = False  # Security mesure so that the thread continue working
            search_target_id, search_target_version = row['assembly_accession'].split('.')
            #search_target = row['assembly_accession'][4:]
            try:  # try/except to check assembly presence 
                fetched_object_from_database = Assembly.objects.get(assembly_id=search_target_id[4:], assembly_version=search_target_version)
                #print('\nQuerry found:\n', index, search_target_id, "got this thing", fetched_object_from_database)
            except Assembly.DoesNotExist:  # try/except to check assembly presence 
                self._write_log("Adding new assembly " + search_target_id + "\n")
                self.updating_status = self._get_update_progress(index)
                #HERE CODE
                try:  # try/except to check species presence 
                    fetched_object_from_database_species = Species.objects.get(ncbi_id=row['taxid'])
                except Species.DoesNotExist:  # try/except to check species presence 
                    taxa_string = self.tax_string_extractor(row['taxid'])
                    print("taxa is:", taxa_string, " ignored are", self.ignore_this_taxa)
                    if len(self.ignore_this_taxa) > 0:  # Ignore this taxa
                        if sum([one_taxa in taxa_string for one_taxa in self.ignore_this_taxa.split(";")]):
                            # Check if if all element that are sprated by a semicolumn are included in taxastring
                            # ignore taxa
                            continue
                    if len(self.do_only_this_taxa) > 0:  # do only this taxa
                        if sum([one_taxa not in taxa_string for one_taxa in self.do_only_this_taxa.split(";")]): 
                            # skip if taxa not present
                            continue
                    # Create new specie
                    self._write_log("Creating new Specie for " +  + "\n")
                    Species.objects.create(species_name=row['organism_name'],
                                            ncbi_id=row['taxid'],
                                            alias=row['asm_name'],
                                            taxonomy=taxa_string
                                            )
                #////////////////////
                # Make directory
                target_directory = os.path.join(
                                                self.UPDATE_LOCATION,
                                                row['assembly_accession'][4:7],
                                                row['assembly_accession'][7:10],
                                                row['assembly_accession'][10:13],
                                                row['assembly_accession'],
                                                'raw_dir'
                                                )
                os.system('mkdir -p ' + target_directory)
                self.updating_status = self._get_update_progress(index)
                # GFF FNA FAA files
                try: 
                    file_names = ["genomic.gff.gz", "genomic.fna.gz", "protein.faa.gz"]
                    for file_name in file_names:
                        file_url = (row['ftp_path']
                                            + '/'
                                            + row['assembly_accession']
                                            + '_'
                                            + row['asm_name'][:40]
                                            +"_"
                                            + file_name
                                            ).replace(" ", "_").replace("(", "_").replace(")", "_").replace("#", "_")

                        file_save_loc = os.path.join(target_directory,
                                                        file_name
                                                    )
                        print("download link check:", file_url)
                        print("save_loc: ", file_save_loc)
                        wget.download(file_url, file_save_loc)  # Thisdoes not work
                        self._write_log(
                                        "Downloaded " 
                                        + file_save_loc
                                        + "sucessfully"
                                        + "\n"
                                        )
                        print("downloaded!")
                        with gzip.open(file_save_loc, 'rb') as f_in:
                            with open(file_save_loc[:-3], 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        os.remove(file_save_loc)
                    # FNA file mySQL
                    print("checkpoint1")

                    Assembly.objects.create(species=Species.objects.get(ncbi_id=row['taxid']),
                                            assembly_id=search_target_id[4:],
                                            assembly_version=search_target_version,
                                            assembly_source="RefSeq",
                                            dir_location=target_directory,
                                            file_location=target_directory+'/genomic.fna',
                                            )
                    self._write_log(
                                    target_directory+'/genomic.fna'
                                    + "\n"
                                    )
                    # gff file mySQL
                    print("checkpoint2")                                                   
                    assembly_instance = Assembly.objects.get(assembly_id=search_target_id[4:],
                                                                                    assembly_version=search_target_version
                                                                                    )     
                    """
                    # this does not work alternative solution is used 
                    Genomicannotation.objects.create(defaults={'assembly':assembly_instance,
                                                                'assembly_version':assembly_instance,
                                                                },
                                                    file_location=target_directory+'/genomic.gff'
                                                    )
                    """
                    self.excute_sql_line(
                            """INSERT INTO GenomicAnnotation(Assembly_ID, Assembly_Version, File_Location) 
                                VALUES ({0}, {1},"{2}");
                            """, [assembly_instance.assembly_id, assembly_instance.assembly_version, target_directory+'/genomic.gff'])
                    self._write_log(
                                    target_directory+'/genomic.gff'
                                    + "\n"
                                    )
                    # faa file mySQL
                    print("checkpoint3")
                    Proteinset.objects.create(annotation=Genomicannotation.objects.get(assembly=search_target_id[4:],
                                                                                    assembly_version=search_target_version
                                                                                    ),
                                                file_type="All",
                                                date_of_the_data = date.today(),
                                                file_location=target_directory+'/protein.faa'
                                                )
                    self._write_log(target_directory+'/protein.faa'
                                    + "\n"
                                    )
                    # json File NEED USE fdog
                    fdog_target_directory = os.path.join(
                                                    self.UPDATE_LOCATION,
                                                    row['assembly_accession'][4:7],
                                                    row['assembly_accession'][7:10],
                                                    row['assembly_accession'][10:13],
                                                    row['assembly_accession'],
                                                    'fdog'
                                                    )
                    os.system('mkdir -p ' + fdog_target_directory)
                    """
                    # Use on system
                    os.system('fdog.addTaxon -f '
                                + file_save_loc[:-3] 
                                + ' -o  '
                                + fdog_target_directory
                                + ' --replace -i '
                                + row['taxid'] 
                                + ' -c'
                                )
                    """
                    # test/${NAME:0:3}/${NAME:3:3}/${NAME:6:3}/GCF_$NAME
                    # Use with SEED 
                    # prepare a table
                    print("path is: ", os.path.join(self.UPDATE_FILES_DIR, "fdog_seed.csv"))
                    with open(os.path.join(self.UPDATE_FILES_DIR, "fdog_seed.csv"), "a") as fdog_file:
                        fdog_file.write(
                                        ",".join([search_target_id, row['taxid'], search_target_version])
                                        + "\n"
                                        )

                    print("Done with ", index)
                    self._job_done = True
                except Exception as e:  # incase download does not work
                    print(" Error occured : ", e)
                    with open(os.path.join(self.UPDATE_FILES_DIR, "error_files.log"), "a") as error_file:
                        error_file.write(
                                        file_url,
                                        + "\n"
                                        )

                print("THIS WORKED !!!! ", search_target_version)

            except Exception as e:  # try/except to check assembly presence 
                print("ERROR 2:", e)
        self.updating_status = self._get_update_progress(index)
        self._stop_me = True  # endfor
        self._job_done = True
        print("stopped/finished", self._stop_me, index)     

    
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
        self._write_log("Downloading the lastest NCBI assembly summary...")
        if os.path.exists(local_path):
            self._write_log("\nOld file still exists, replacing old file...")
            os.remove(local_path)
        else:
            wget.download(refseq_url, local_path)
        self._write_log("successfull!\n")
        self.downloaded_assembly_summary_path = os.path.join(local_path, 'assembly_summary_refseq.txt')
        if Path(self.downloaded_assembly_summary_path).is_file:
            print("Assembly downloaded successfully!")
        else:
            print("Assembly downloaded failed!")
            raise ("Could not download file.")


    def excute_sql_line(self, mysql_line, mysql_values = []):  
        """
        execute a mySQL commant using Values with formating sting
        """
        try:
            self.conn = connect(user=DATABASES['default']['USER'],
                                password=DATABASES['default']['PASSWORD'],
                                host=DATABASES['default']['HOST'],
                                database=DATABASES['default']['NAME'],
                                autocommit=True
                                   )
            self.my_cursor = self.conn.cursor(buffered=True)
            self.my_cursor.execute("Use "+ DATABASES['default']['NAME'] + ";")
            self.my_cursor.execute(mysql_line.format(*mysql_values))   
        except:
            print("MySQL command error! ")


    def _get_update_progress(self, my_index) -> int:
        if my_index>self.data_volume:
            print("Update progress Error!")
            return -1
        if self.data_volume == 0:
            return 100
        print ("current prog",  my_index, int(my_index/self.data_volume*100))
        return int(my_index/self.data_volume*100)


    def readdata(self):
        """
        Reads "assembly_summary_refseq.txt" filters out non needed data
            non Representative will be deleted 
            non necessary collumn will be dropped 
        _______________
        Input:  self.assembly_df -> PandaDataFrame
                self.downloaded_assembly_summary_path -> string
        _______________
        output: self.assembly_df
                self.data_volume : len of the df
        _______________
        Returns: None
        _______________
        Imports:
            pandas
        """        
        self._write_log += "Filtering the assembly summary...\n"
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
        self.assembly_df.drop(
                self.assembly_df[self.assembly_df['refseq_category']=='na'].index,
                inplace=True,
                axis=0
                )
        self.assembly_df.rename(columns={ self.assembly_df.columns[0]: "assembly_accession" }, inplace = True)
        self.data_volume = len(self.assembly_df)


    def tax_string_extractor(self, specie_taxid, my_email="change_me_if_you_want@mail.py"):
        """  
        args:
            specie_taxid: NCBI taxID (example 9606)
        imports: 
            from Bio import Entrez
            import xml.etree.ElementTree as ET
        """
        Entrez.email = my_email
        handle = Entrez.efetch(db="taxonomy", id=specie_taxid, retmode='xml')
        raw_data = handle.read().decode()
        root = ET.fromstring(raw_data)
        handle.close()
        
        for taxon in root:
            for child in taxon:
                if child.tag == 'Lineage':
                    linstring = child.text
        return linstring


    def unzip_gz_file(self,
                    source_path,
                    save_path=r"C:\Users\Amine\Documents\GoetheUni\MASTERARBEIT\test"):
        """Download and extracts gz files

        Args:
            source_path (string): link to download from
            save_path (string): Where to save the file. Defaults to "C:/Users/Amine/Documents/GoetheUni/MASTERARBEIT/test".
        
        Imports:
            gzip
            wget
        """
        print("here!!!!! download_gz_file")
        #super_path = "{basepath}/{name}/{file_name}".format()
        wget.download(source_path, save_path)
        with gzip.open(source_path, 'rb') as f_in:
            with open(save_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    def _write_log(self, text_output):
        self.html_print += text_output
        with open(os.path.join(self.UPDATE_FILES_DIR, "my_last_update.log"), "a") as update_file:
                        update_file.write(text_output)

if __name__=="__main__":
    print("What are you doing?")
    #test=SuperUpdate()
