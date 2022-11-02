# -*- coding: utf-8 -*-
"""
Requires AdditionalData folder
    
Just filles the Data using links from a txt files and 
some addition information also stored in txt files 
Fills Species and assembly table
Fills all

Last Modified 14.02.2022
@author: Amine
"""
__version__ = "2.2"
from mysql.connector import connect, Error
from os import listdir
from os.path import join


class UltimateSQLFiller():
    """
    version
    Main Class
    """
    def __init__(self, database = "Genomes"):
        """
        Returns
        -------
        None.

        """
        self.database_name = database
        self.BlastDB_set = set()
        self.error_lines = []
        self.not_found_values = []
        self.taxa_not_found = []
        self.data_base_connection()
        self.spiecies_extractorV3()   
        self.fill_species_assemblies_tables()
        print("Species Table Filled!")
        print("Assemblies Table Filled!")
        self.browse_data()
        print("Data Saved successfully!")
        
        
    def data_base_connection(self):
        """
        --- CHANGE DATABASE IF NEEDED ---
        Connects to the data base 

        Returns
        -------
        None.

        """
        try:
            self.conn = connect(user='amine',
                                password='ChangeMe1234',
                                host='172.17.100.21',
                                database= self.database_name
                                   )
            self.my_cursor = self.conn.cursor(buffered=True)
            self.my_cursor.execute("Use "+ self.database_name + ";")
            self.conn.autocommit = True
            print("Connected sucessfully")
        except:
            print("Connection error")
        
            
    def excute_sql_line(self, mysql_line, mysql_values = []):  
        """
        uses  self.my_cursor to excute SQl commands
        
        Returns
        -------
        None.   
        """
        try:
            self.my_cursor.execute(mysql_line.format(*mysql_values))   
        except Error as error:
            print("Something went wrong: {}".format(error))
            print(mysql_line.format(*mysql_values))
            self.error_lines += [(mysql_line, mysql_values)] 
        except Exception as error:
            self.error_lines += [(mysql_line, mysql_values)]
            print("An Error has occured:" ,mysql_line, mysql_values)
            print("________________")
            print(type(error))    # the exception instance
            print("________________")
            print(error.args)     # arguments stored in .args
            print("________________")
            print(error) 
            assert(0)
        
        
    def fill_species_assemblies_tables(self):
        """
        Fills the species table using the dictionary already filled
        Fills the assembly table using the dictionary already filled
        Requires: self.species_data_dict
        Returns
        -------
        None.

        """
        specie_id = 0
        for my_values in self.species_data_dict.values():
            self.excute_sql_line(
                    """INSERT INTO Species(NCBI_ID, Species_Name, Category) 
                    VALUES ({0},"{1}","{5}");
                    """, 
                    my_values
                    )  # Fill spieces table
            # Just in case needed SELECT LAST_INSERT_ID() FROM species;
            #specie_id += 1
            self.excute_sql_line(
                    "SELECT LAST_INSERT_ID() FROM Species;"
                    )
            specie_id = self.my_cursor.fetchone()[0] 
            #print("helllo !!!", specie_id, type(specie_id))
            specie_GCF= my_values[2]
            self.excute_sql_line(
                    """INSERT INTO Assembly(Species, Assembly_ID, Assembly_Version, File_Location, Assembly_Source) 
                    VALUES ({0},{1},{2},"{3}","RefSeq");""", 
                    [specie_id, 
                     specie_GCF[specie_GCF.index('_')+1:specie_GCF.index('.')], 
                     specie_GCF[specie_GCF.index('.')+1:],
                     "UNKNOWN"
                     ]
                    )  # Fill assembly table
            if specie_GCF not in self.taxa_data_dict :
                self.taxa_not_found += [specie_GCF]
            else:
                self.excute_sql_line(
                        """UPDATE Species SET taxonomy="{0}" WHERE Species_ID={1};""", 
                        [self.taxa_data_dict[specie_GCF], specie_id]
                        )  # Fill taxa in species table
               
        
    def browse_data(self):
        """
        uses the data in self.input_file to fill the data base tables
            - Assembly
            - genomic annotation
            - ProteinSet
            - featureAnnotation
            - Blast DB
        For nonMammalianVertebratesRefSeq only active_June21
        For Bacteria only unique_GCF_June21
        For Archaea only unique_IDs
        
        
        Returns 
        -------
        None.

        """
        
        self.ignored_files = []
        self.nonM_actJune = []
        self.Bact_UniqJune = []
        self.Archaea_UniqID = []
        self.others_rawdir = []
        with open('pureged_all_files.txt', 'r') as self.input_file:
            self.file_lines = self.input_file.readlines()

        #### Fill the gene Annotations and update the assembly table (gff and fna files)  ####
        print("Checkpoint 1")
        counter_s = 0
        for line in self.file_lines[::-1]:
            counter_s += 1
            if counter_s%1000==0:
                print("Loading: ", counter_s//1000, "%")
            #continue ##################################################
            my_file = line.split('/')
            #print(my_file)
            if "raw_dir" in my_file[-4]:  # raw_dir directory
                specie_GCF = my_file[-2]
                if "nonMammalianVertebratesRefSeq" in my_file[-5]:  
                    if "active_June21" in my_file[-3]: 
                        if "genomic.fna" in my_file[-1]:
                            my_values = [specie_GCF[specie_GCF.index('_')+1:specie_GCF.index('.')],
                                         specie_GCF[specie_GCF.index('.')+1:],
                                         line[:-12],
                                         line[:-1]]
                            self.update_Assembly_table(my_values)
                            self.file_lines.remove(line)  # win time for the next loop
                        elif "genomic.gff" in my_file[-1]:
                            my_values = [specie_GCF[specie_GCF.index('_')+1:specie_GCF.index('.')],
                                         specie_GCF[specie_GCF.index('.')+1:],
                                         line[:-1]]
                            self.fill_genomicannotation_table(my_values)
                            self.file_lines.remove(line)  # win time for the next loop
                        else:
                            self.nonM_actJune.append(my_file)
                elif "Bacteria" in my_file[-5]:
                    if "unique_GCF_June21" in my_file[-3]: 
                        if "genomic.fna" in my_file[-1]:
                            my_values = [specie_GCF[specie_GCF.index('_')+1:specie_GCF.index('.')],
                                         specie_GCF[specie_GCF.index('.')+1:],
                                         line[:-12],
                                         line[:-1]]
                            self.update_Assembly_table(my_values)
                            self.file_lines.remove(line)  # win time for the next loop
                        elif "genomic.gff" in my_file[-1]:
                            my_values = [specie_GCF[specie_GCF.index('_')+1:specie_GCF.index('.')],
                                         specie_GCF[specie_GCF.index('.')+1:],
                                         line[:-1]]
                            self.fill_genomicannotation_table(my_values)
                            self.file_lines.remove(line)  # win time for the next loop
                        else:
                            self.Bact_UniqJune.append(my_file)
                elif "Archaea" in my_file[-5]:
                    if "unique_IDs" in my_file[-3]: 
                        if "genomic.fna" in my_file[-1]:
                            my_values = [specie_GCF[specie_GCF.index('_')+1:specie_GCF.index('.')],
                                         specie_GCF[specie_GCF.index('.')+1:],
                                         line[:-12],
                                         line[:-1]]
                            self.update_Assembly_table(my_values)
                            self.file_lines.remove(line)  # win time for the next loop
                        elif "genomic.gff" in my_file[-1]:
                            my_values = [specie_GCF[specie_GCF.index('_')+1:specie_GCF.index('.')],
                                         specie_GCF[specie_GCF.index('.')+1:],
                                         line[:-1]]
                            self.fill_genomicannotation_table(my_values) 
                            self.file_lines.remove(line)  # win time for the next loop
                        else:
                            self.Archaea_UniqID.append(my_file)
                            
                else:
                    if "genomic.fna" in my_file[-1]:
                        my_values = [specie_GCF[specie_GCF.index('_')+1:specie_GCF.index('.')],
                                     specie_GCF[specie_GCF.index('.')+1:],
                                     line[:-12],
                                     line[:-1]]
                        self.update_Assembly_table(my_values)
                        self.file_lines.remove(line)  # win time for the next loop
                    elif "genomic.gff" in my_file[-1]:
                        my_values = [specie_GCF[specie_GCF.index('_')+1:specie_GCF.index('.')],
                                     specie_GCF[specie_GCF.index('.')+1:],
                                     line[:-1]]
                        self.fill_genomicannotation_table(my_values)
                        self.file_lines.remove(line)  # win time for the next loop
                    else:
                        self.others_rawdir.append(my_file)
            else:
                #print("WOW:", line)
                pass
        # End for (gff and fna)
        #### Fill the protein table (fa and faa files)  ####    
        print("Checkpoint 2")
        for line in self.file_lines[::-1]:  # now protein
            #continue ##################################################
            my_file = line.split('/')
            #print(my_file)
            if "raw_dir" in my_file[-4]:  # raw_dir directory
                specie_GCF = my_file[-2]
                if "nonMammalianVertebratesRefSeq" in my_file[-5]:  
                    if "active_June21" in my_file[-3]: 
                        if "protein.faa" in my_file[-1]:
                            my_values = [specie_GCF[specie_GCF.index('_')+1:specie_GCF.index('.')],
                                         specie_GCF[specie_GCF.index('.')+1:],
                                         line[:-1],
                                         "All"]
                            self.fill_proteinset_table(my_values)
                            self.file_lines.remove(line)  # win time for the next loop
                        elif "protein.rep.fa" in my_file[-1]:
                            my_values = [specie_GCF[specie_GCF.index('_')+1:specie_GCF.index('.')],
                                         specie_GCF[specie_GCF.index('.')+1:],
                                         line[:-1],
                                         "Representative"]
                            self.fill_proteinset_table(my_values)
                            self.file_lines.remove(line)  # win time for the next loop
                        else:
                            pass
                elif "Bacteria" in my_file[-5]:
                    if "unique_GCF_June21" in my_file[-3]: 
                        if "protein.faa" in my_file[-1]:
                            my_values = [specie_GCF[specie_GCF.index('_')+1:specie_GCF.index('.')],
                                         specie_GCF[specie_GCF.index('.')+1:],
                                         line[:-1],
                                         "All"]
                            self.fill_proteinset_table(my_values)
                            self.file_lines.remove(line)  # win time for the next loop 
                        elif "protein.rep.fa" in my_file[-1]:
                            my_values = [specie_GCF[specie_GCF.index('_')+1:specie_GCF.index('.')],
                                         specie_GCF[specie_GCF.index('.')+1:],
                                         line[:-1],
                                         "Representative"]
                            self.fill_proteinset_table(my_values)
                            self.file_lines.remove(line)  # win time for the next loop
                        else:
                            pass
                elif "Archaea" in my_file[-5]:
                    if "unique_IDs" in my_file[-3]: 
                        if "protein.faa" in my_file[-1]:
                            my_values = [specie_GCF[specie_GCF.index('_')+1:specie_GCF.index('.')],
                                         specie_GCF[specie_GCF.index('.')+1:],
                                         line[:-1],
                                         "All"]
                            self.fill_proteinset_table(my_values)
                            self.file_lines.remove(line)  # win time for the next loop
                        elif "protein.rep.fa" in my_file[-1]:
                            my_values = [specie_GCF[specie_GCF.index('_')+1:specie_GCF.index('.')],
                                         specie_GCF[specie_GCF.index('.')+1:],
                                         line[:-1],
                                         "Representative"]
                            self.fill_proteinset_table(my_values)
                            self.file_lines.remove(line)  # win time for the next loop
                        else:
                            pass
                else:
                    if "protein.faa" in my_file[-1]:
                        my_values = [specie_GCF[specie_GCF.index('_')+1:specie_GCF.index('.')],
                                     specie_GCF[specie_GCF.index('.')+1:],
                                     line[:-1],
                                     "All"]
                        self.fill_proteinset_table(my_values)
                        self.file_lines.remove(line)  # win time for the next loop
                    elif "protein.rep.fa" in my_file[-1]:
                        my_values = [specie_GCF[specie_GCF.index('_')+1:specie_GCF.index('.')],
                                     specie_GCF[specie_GCF.index('.')+1:],
                                     line[:-1],
                                     "Representative"]
                        self.fill_proteinset_table(my_values)
                        self.file_lines.remove(line)  # win time for the next loop
                    else:
                        pass

            else:
                self.ignored_files.append(my_file)
        #End for (faa / fa files)  ####     
        #### Fill the protein featuretable (json)  and blast  ####  
        print("Checkpoint 3")        
        for line in self.file_lines:
            my_file = line.split('/')
            if ".json" in my_file[-1] and "@" in my_file[-1]:
                # print("GCF_"+my_file[-1])
                # print("GCF_"+my_file[-1]\
                #     [ my_file[-1][ my_file[-1].index("@")+1: 
                #                   ].index("@") +my_file[-1].index("@")+2:-6]\
                #          .replace("_","."))
                my_values = my_file[-1]\
                     [ my_file[-1][ my_file[-1].index("@")+1: 
                                   ].index("@") +my_file[-1].index("@")+2:-6]\
                          .split("_") + [line[:-1]]
                self.fill_featureannotation_table(my_values)
            elif "blast_dir" in my_file[-3]:
                if my_file[-2] not in self.BlastDB_set:
                    my_values = my_file[-1]\
                         [ my_file[-1][ my_file[-1].index("@")+1: 
                                       ].index("@") +my_file[-1].index("@")+2:my_file[-1].index(".")]\
                              .split("_") + ["/".join(my_file[:-1])]
                    self.fill_blastdb_table(my_values)
                    self.BlastDB_set.add(my_file[-2])
        
            else:
                pass
          
    
    def fill_genomicannotation_table(self, my_values):    
        sql = """INSERT INTO GenomicAnnotation(Assembly_ID, Assembly_Version, File_Location) 
                VALUES ({0}, {1},"{2}");"""
        self.excute_sql_line(sql, my_values)


    def fill_proteinset_table(self, my_values):
        self.excute_sql_line("""Select Annotation_ID from GenomicAnnotation 
        where Assembly_ID = {0}
        and Assembly_Version = {1};""", my_values)
        try:
            my_values += [self.my_cursor.fetchone()[0]] 
            sql = """INSERT INTO ProteinSet(Annotation_ID, file_type, File_Location) VALUES ({4}, "{3}","{2}");"""
            self.excute_sql_line(sql, my_values)
        except:
            print("error while filling proteinset table")
            print(my_values)
            self.not_found_values.append(["Protein"]+my_values[:2])
 
    
    def fill_blastdb_table(self, my_values):
        """
        Fills the Blast BD table

        Parameters
        ----------
        my_values : List
            contains different values to be included in the database.

        Returns
        -------
        None.

        """
        self.excute_sql_line("""SELECT Protein_ID FROM GenomicAnnotation 
                            inner join  ProteinSet 
                            on ProteinSet.Annotation_ID = GenomicAnnotation.Annotation_ID 
                            where Assembly_ID = {0}
                            and Assembly_Version = {1};""", my_values)
        try:
            my_values += [self.my_cursor.fetchone()[0]] 
            sql = """INSERT INTO BlastDB(Protein_ID, Dir_Location) VALUES ({3},"{2}");"""
            self.excute_sql_line(sql, my_values)
        except:
            self.not_found_values.append(["Blast"]+my_values[:2])

            
        
        
    def update_Assembly_table(self, my_values):  
        self.excute_sql_line("""UPDATE Assembly 
                                SET
                                	Dir_Location = "{2}",
                                	File_Location = "{3}"
                                where Assembly_ID = {0}
                                and Assembly_Version = {1};""", my_values)
        
    
    def fill_featureannotation_table(self, my_values):
        """
        Fills the FeatureAnnotation table

        Parameters
        ----------
        my_values : List
            contains different values to be included in the database.

        Returns
        -------
        None.

        """
        self.excute_sql_line("""SELECT Protein_ID FROM GenomicAnnotation 
                            inner join  ProteinSet 
                            on ProteinSet.Annotation_ID = GenomicAnnotation.Annotation_ID 
                            where Assembly_ID = {0}
                            and Assembly_Version = {1};""", my_values)
        try:
            my_values += [self.my_cursor.fetchone()[0]]   
            sql = """INSERT INTO FeatureAnnotation(Protein_ID, File_Location) VALUES ({3},"{2}");"""
            self.excute_sql_line(sql, my_values)
        except:
            self.not_found_values.append(["Feature"]+my_values[:2])
            print("Error 12 feature annotation")

                    
    def fill_noncodingrna_table(self, my_values):
        """
        NOT READY !!!! 

        Parameters
        ----------
        my_values : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        try:
            sql = """INSERT INTO NonCodingRNA(Species_Name, Species_ID, NCBI_ID) VALUES ("{0}","{1}",{2});"""
            self.my_cursor.execute(sql.format(my_values))
        except:
            print("error")
            self.my_cursor.execute("""SELECT * FROM species;""")
            print("here", self.my_cursor.fetchall())
    
        
    def spiecies_extractorV3(self, my_location = "AdditionalData", taxa_file_path="all_taxa_string.txt"):
        """
        Checks  all the files in a specific location and 
        PS: Be carful about teh length of file name
        
        Parameters
        ----------
        my_location : String
            Path to the folder
            
        Returns
        -------
        None 
        (but ceates a dictionary : self.species_data_dict
         and a list: self.files_list)
        creates  self.taxa_data_dict
            
        
        """
        self.files_list = [join(my_location, f) \
                            for f in listdir(my_location) 
                            ]
        self.species_data_dict = {}
        for each_file in self.files_list:
            file_name = each_file.split("\\")[-1]
            with open(each_file, 'r') as self.input_file:
                for line in self.input_file:
                    my_list = line.split("|")+ [file_name[:-20]] # Files name will be added referting to spices subgroup
                    if 'active' in my_list[-2]:
                        exec("self.species_data_dict[\"{assembly_accession}\"] = {species_list}".format(
                        assembly_accession = my_list[2],
                        species_list = my_list))
        self.taxa_data_dict = {}
        with open(taxa_file_path, 'r') as self.taxa_file:
            for line in self.taxa_file:
                my_taxa_data = line[:-1].split(";")
                if 'GCF' in my_taxa_data[-3]:
                    self.taxa_data_dict[ my_taxa_data[-3] ] = ";".join(my_taxa_data[:-5])
                else:
                    self.taxa_data_dict[ my_taxa_data[-4] ] = ";".join(my_taxa_data[:-6])
                
            
        
if __name__ == "__main__":    
    Test = UltimateSQLFiller()
