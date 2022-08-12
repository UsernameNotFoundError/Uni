__author__ = "Amine"
from argparse import ONE_OR_MORE
from datetime import date
import wget  # Download files from url
import gzip  # unzif gz files
import shutil
import pandas as pd
from pathlib import Path
import os
from mainapp.models import Assembly, Species, Genomicannotation, Proteinset
from mysql.connector import connect  # in case model doe not work
from Uni.settings import DATABASES, MEDIA_DIR
from Bio import Entrez
import xml.etree.ElementTree as ET
import glob


class SuperUpdate():
    """
    This class contains the modules reponsible for the database updates
    """
    _version = 2.0
    BASE_DIR = Path(__file__).resolve().parent.parent
    UPDATE_FILES_DIR = os.path.join(BASE_DIR,'media/updateapp/')
    UPDATE_LOCATION = "/mnt/c/Users/Amine/Documents/GoetheUni/MASTERARBEIT/test/" # Change me

    def __init__(self, ignore_this_taxa="" , do_only_this_taxa="") -> None:
        print("START THREAD")
        self.updating_status = 0
        self._stop_me = False
        self.html_print = ""
        self.ignore_this_taxa = ignore_this_taxa
        self.do_only_this_taxa = do_only_this_taxa
        self._job_done = False
        self._write_log("Update log of" + str(date.today()) +".\n", new_update=True)


    def _start_update(self):
        """
        Called with an other thread to ensure simultaneous execution 
        """
        if self._stop_me:
            print("Update not initiated!")
            return
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
        for index, my_tuple in enumerate(self.assembly_df.iterrows()):
            row = my_tuple[1]
            print("Progressing: ", index, row)
            if index%500 == 0:
                self.updating_status = self._get_update_progress(index)
            if self._stop_me:
                self._write_log("Job was interrupted...\n")
                break
            self._job_done = False  # Security mesure so that the thread continue working
            search_target_id, search_target_version = row['assembly_accession'].split('.')
            #search_target = row['assembly_accession'][4:]
            try:  # try/except to check assembly presence 
                fetched_object_from_database = Assembly.objects.get(assembly_id=search_target_id[4:], assembly_version=search_target_version)
                print('\nQuerry found:\n', index, search_target_id, "got this thing", fetched_object_from_database)
            except Assembly.DoesNotExist:  # try/except to check assembly presence 
                #HERE CODE
                try:  # try/except to check species presence 
                    fetched_object_from_database_species = Species.objects.get(ncbi_id=row['taxid'])
                    taxa_string = fetched_object_from_database_species.taxonomy
                    if len(self.ignore_this_taxa) > 0:  # Ignore this taxa
                        if sum([one_taxa in taxa_string for one_taxa in self.ignore_this_taxa.split(";")]):
                            print("taxa is:", taxa_string, " ignored are", self.ignore_this_taxa)
                            # Check if if all element that are sprated by a semicolumn are included in taxastring
                            # ignore taxa
                            self._job_done = True
                            continue
                    if len(self.do_only_this_taxa) > 0:  # do only this taxa
                        if sum([one_taxa not in taxa_string for one_taxa in self.do_only_this_taxa.split(";")]): 
                            # skip if taxa not present
                            self._job_done = True
                            continue
                    self._write_log("Adding new assembly " + search_target_id + "\n")
                    self.updating_status = self._get_update_progress(index)
                except Species.DoesNotExist:  # try/except to check species presence 
                    taxa_string = self.tax_string_extractor(row['taxid'])
                    if len(self.ignore_this_taxa) > 0:  # Ignore this taxa
                        if sum([one_taxa in taxa_string for one_taxa in self.ignore_this_taxa.split(";")]):
                            print("taxa is:", taxa_string, " ignored are", self.ignore_this_taxa)
                            # Check if if all element that are sprated by a semicolumn are included in taxastring
                            # ignore taxa
                            self._job_done = True
                            continue
                    if len(self.do_only_this_taxa) > 0:  # do only this taxa
                        if sum([one_taxa not in taxa_string for one_taxa in self.do_only_this_taxa.split(";")]): 
                            # skip if taxa not present
                            self._job_done = True
                            continue
                    # Create new specie
                    self._write_log("Creating new Specie for " +  + "\n")
                    self.updating_status = self._get_update_progress(index)
                    Species.objects.create(species_name=row['organism_name'],
                                            ncbi_id=row['taxid'],
                                            alias=row['asm_name'],
                                            taxonomy=taxa_string
                                            )
                #////////////////////
                # Make directory
                self._write_log("Making new directory for new assembly " + search_target_id + "... ")
                target_directory = os.path.join(
                                                self.UPDATE_LOCATION,
                                                row['assembly_accession'][4:7],
                                                row['assembly_accession'][7:10],
                                                row['assembly_accession'][10:13],
                                                row['assembly_accession'],
                                                'raw_dir'
                                                )
                os.system('mkdir -p ' + target_directory)
                self._write_log("successfull.\n")
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
                                        + " sucessfully"
                                        + "\n"
                                        )
                        print("downloaded!")
                        # unpack the file
                        with gzip.open(file_save_loc, 'rb') as f_in:
                            with open(file_save_loc[:-3], 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        os.remove(file_save_loc)  # Delete the uncompressed version
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
                                    "DB path added: "
                                    + target_directory+'/genomic.fna'
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
                                    "DB path added: "
                                    + target_directory+'/genomic.gff'
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
                    self._write_log(
                                    "DB path added: "
                                    + target_directory+'/protein.faa'
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
            print("Out for loop")

        self.updating_status = self._get_update_progress(index)
        self._stop_me = True  # endfor
        self._job_done = True
        print("stopped/finished", self._stop_me, index)     

    
    def clear_cache(self):
        """delete update files
        """
        for one_file in os.listdir(self.UPDATE_FILES_DIR):
            os.remove(os.path.join(dir, one_file))


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
        if os.path.exists(local_path+"/assembly_summary_refseq.txt"):
            self._write_log("\nOld file still exists, replacing old file...")
            os.remove(local_path+"/assembly_summary_refseq.txt")
            print("ping1")
            wget.download(refseq_url, local_path)
            print("pong1")
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


    def fdog_luncher(self, slurm_sript):
        """
        This function use the cluster to create the protein's annotations (json) and blast dir
        """
        # In case fdog_seed is too big it will be split 
        small_files_list = []
        with open(self.UPDATE_FILES_DIR+"fdog_seed.csv", "r") as big_file:
            # update database
            for i, line in enumerate(big_file):
                # Split files for cluster run
                if i % 1000 == 0:
                    small_files_list += [self.UPDATE_FILES_DIR+"small_fdog_file_{}.csv".format(i//1000)]
                with open(small_files_list[-1], "a") as small_file:
                    small_file.write(line)


        # run all fdog on the cluster
        for fdog_file in small_files_list:
            #create slurm_file
            slurm_file_path = self.UPDATE_FILES_DIR+"fdog_seed.slurm"
            with open(slurm_file_path, "w") as slurm_file:  #change me
                slurm_file.write(slurm_sript.replace("\r", "").replace("[my_file]", fdog_file).replace("[my_lines]", "1-"+str(open(fdog_file).read().count("\n"))))

            os.system("sbatch " + slurm_file_path)
        return


    def _get_update_progress(self, my_index) -> int:
        if my_index>self.data_volume:
            print("Update progress Error!")
            return -1
        if self.data_volume == 0:
            return 100
        print ("current prog",  my_index, int(my_index/self.data_volume*100))
        return int(my_index/self.data_volume*100)


    def mySQL_add_annotations_and_blast() -> None:
        """
        Adds the newly made json files and blastdir to the database
        """
        with open(MEDIA_DIR+"/updateapp/fdog_seed.csv", "r") as my_input_file:
            my_input_data = my_input_file.readlines()
            
        for line in my_input_data:
            if len(line) < 2:
                break
            my_values = line[:-1].split(",")
            try:
                print(my_values)
                conn = connect( user=DATABASES['default']['USER'],
                                password=DATABASES['default']['PASSWORD'],
                                host=DATABASES['default']['HOST'],
                                database=DATABASES['default']['NAME'],
                                autocommit=True
                                )
                my_cursor = conn.cursor(buffered=True)
                my_cursor.execute("Use "+ DATABASES['default']['NAME'] + ";")
                my_cursor.execute(
                        """SELECT ProteinSet.Protein_ID
                        FROM Assembly
                        JOIN Species
                        ON Assembly.Species=Species.Species_id
                        JOIN GenomicAnnotation
                        ON Assembly.Assembly_ID=GenomicAnnotation.Assembly_ID AND Assembly.Assembly_version=GenomicAnnotation.Assembly_version
                        join ProteinSet
                        on GenomicAnnotation.Annotation_ID=ProteinSet.Annotation_ID
                        WHERE NCBI_ID = {1} and Assembly.Assembly_version= {2};""".format(*my_values)
                        )   
                
                my_fdog_dir = os.path.join("/share/gluster/GeneSets/NCBI-Genomes/",
                            my_values[0][4:7],
                            my_values[0][7:10],
                            my_values[0][10:13],
                            my_values[0] + '.' + my_values[2],
                            'fdog'
                            )
                            
                os.chdir(my_fdog_dir+"/weight_dir")    
                json_file = my_fdog_dir + "/weight_dir/" + glob.glob("*.json")[0]

                            
                my_target_protein_id = my_cursor.fetchone()[0]
                print("check 1:", my_target_protein_id)
                my_cursor.execute(
                        "INSERT INTO FeatureAnnotation(Protein_ID, Tool, File_Location) VALUES({0}, 'fdog', '{1}');".format(*[my_target_protein_id, json_file])
                        )  # FeatureAnnotation
                my_cursor.execute(
                        "INSERT INTO BlastDB(Protein_ID, Dir_Location) VALUES({0}, '{1}');".format(*[my_target_protein_id, my_fdog_dir+"/blast_dir"])
                        )  # BlastDB

            except Exception as e:
                print("MySQL command error! \n", e)


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
        self._write_log("Filtering the assembly summary...\n")
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


    def _write_log(self, text_output, new_update=False):
        if new_update:
            with open(os.path.join(self.UPDATE_FILES_DIR, "my_last_update.log"), "w") as update_file:
                update_file.write(text_output)
        else:
            self.html_print += text_output
            my_log_file = os.path.join(self.UPDATE_FILES_DIR, "my_last_update.log")

            with open(os.path.join(self.UPDATE_FILES_DIR, "my_last_update.log"), "a") as update_file:
                update_file.write(text_output)

if __name__=="__main__":
    print("What are you doing?")
    #test=SuperUpdate()
