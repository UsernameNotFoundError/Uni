from mysql.connector import connect
from Uni.settings import DATABASES
from mainapp.models import Searchregister, Searchresults
#from win32com.client import Dispatch

class BigBrain():
    """Main class that contains diffrent functions
        for database querries
    """
    def __init__(self, user):
        self.user = user
        self.data_base_connection()
        self.search_results = []
        self.search_columns = []
        self.search_querry = []
        # SQL_COMMANDS :
        # 0 : uses NCBI ID
        # 1 : uses species_name
        # 2 : uses GCF
        # 3 : uses taxonomy
        # Commands for fna files
        self.SQL_COMMANDS = [
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, assembly.File_Location
                FROM assembly
                INNER JOIN species
                ON assembly.species=species.species_id  where NCBI_ID = {0};""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, assembly.File_Location
                FROM assembly
                INNER JOIN species
                ON assembly.species=species.species_id where species_name LIKE "{0}%"  OR Species.taxonomy LIKE "%{0}%";""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, assembly.File_Location
                FROM assembly
                INNER JOIN species
                ON assembly.species=species.species_id  where Assembly_ID = {0} and assembly_version = {1};""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id,species.species_name, species.alias,  assembly.Assembly_Source, assembly.File_Location
                FROM assembly
                INNER JOIN species
                ON assembly.species=species.species_id  WHERE Species.taxonomy LIKE "%{0}%";""",
                ]
        # gff files
        self.SQL_COMMANDS_1 = [
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, genomicannotation.File_Location
                FROM assembly
                INNER JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                WHERE NCBI_ID = {0};""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, genomicannotation.File_Location
                FROM assembly
                INNER JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                WHERE species_name LIKE "{0}%" OR Species.taxonomy LIKE "%{0}%";""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, genomicannotation.File_Location
                FROM assembly
                INNER JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                WHERE assembly.Assembly_ID = {0} and assembly.assembly_version = {1};""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, genomicannotation.File_Location
                FROM assembly
                INNER JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                WHERE  Species.taxonomy  LIKE "%{0}%";""",
                ]
        # fa files
        self.SQL_COMMANDS_2 = [
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, proteinset.File_Location
                FROM assembly
                JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                join proteinset
                on genomicannotation.Annotation_ID=proteinset.Annotation_ID
                WHERE NCBI_ID = {0} and proteinset.file_type="all";""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, proteinset.File_Location
                FROM assembly
                JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                join proteinset
                on genomicannotation.Annotation_ID=proteinset.Annotation_ID
                WHERE species_name LIKE "{0}%" OR Species.taxonomy LIKE "%{0}%" and proteinset.file_type="all";""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, proteinset.File_Location
                FROM assembly
                JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                join proteinset
                on genomicannotation.Annotation_ID=proteinset.Annotation_ID
                WHERE assembly.Assembly_ID = {0} and assembly.assembly_version = {1} and proteinset.file_type="all";""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, proteinset.File_Location
                FROM assembly
                JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                join proteinset
                on genomicannotation.Annotation_ID=proteinset.Annotation_ID
                WHERE Species.taxonomy LIKE "%{0}%" and proteinset.file_type="all";""",
                ]
        # faa files
        self.SQL_COMMANDS_3 = [
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, proteinset.File_Location
                FROM assembly
                JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                join proteinset
                on genomicannotation.Annotation_ID=proteinset.Annotation_ID
                WHERE NCBI_ID = {0} AND proteinset.file_type='Representative';""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, proteinset.File_Location
                FROM assembly
                JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                join proteinset
                on genomicannotation.Annotation_ID=proteinset.Annotation_ID
                WHERE species_name LIKE "{0}%" OR Species.taxonomy LIKE "%{0}%" AND proteinset.file_type='Representative';""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, proteinset.File_Location
                FROM assembly
                JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                join proteinset
                on genomicannotation.Annotation_ID=proteinset.Annotation_ID
                WHERE assembly.Assembly_ID = {0} and assembly.assembly_version = {1} AND proteinset.file_type='Representative';""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, proteinset.File_Location
                FROM assembly
                JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                join proteinset
                on genomicannotation.Annotation_ID=proteinset.Annotation_ID
                WHERE Species.taxonomy LIKE "%{0}%" AND proteinset.file_type='Representative';""",
                ]
        # json files
        self.SQL_COMMANDS_4 = [
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, featureannotation.File_Location
                FROM assembly
                JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                join proteinset
                on genomicannotation.Annotation_ID=proteinset.Annotation_ID
                join featureannotation
                on featureannotation.Protein_ID=proteinset.Protein_ID
                WHERE NCBI_ID = {0};""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, featureannotation.File_Location
                FROM assembly
                JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                join proteinset
                on genomicannotation.Annotation_ID=proteinset.Annotation_ID
                join featureannotation
                on featureannotation.Protein_ID=proteinset.Protein_ID
                WHERE species_name LIKE "{0}%" OR Species.taxonomy LIKE "%{0}%";""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, featureannotation.File_Location
                FROM assembly
                JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                join proteinset
                on genomicannotation.Annotation_ID=proteinset.Annotation_ID
                join featureannotation
                on featureannotation.Protein_ID=proteinset.Protein_ID
                WHERE assembly.Assembly_ID = {0} and assembly.assembly_version = {1};""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, featureannotation.File_Location
                FROM assembly
                JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                join proteinset
                on genomicannotation.Annotation_ID=proteinset.Annotation_ID
                join featureannotation
                on featureannotation.Protein_ID=proteinset.Protein_ID
                WHERE Species.taxonomy LIKE "%{0}%";""",
                ]
        # BlastDB files
        self.SQL_COMMANDS_5 = [
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, blastdb.Dir_Location
                FROM assembly
                JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                join proteinset
                on genomicannotation.Annotation_ID=proteinset.Annotation_ID
                join blastdb
                on blastdb.Protein_ID=proteinset.Protein_ID
                WHERE NCBI_ID = {0};""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, blastdb.Dir_Location
                FROM assembly
                JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                join proteinset
                on genomicannotation.Annotation_ID=proteinset.Annotation_ID
                join blastdb
                on blastdb.Protein_ID=proteinset.Protein_ID
                WHERE species_name LIKE "{0}%" OR Species.taxonomy LIKE "%{0}%";""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, blastdb.Dir_Location
                FROM assembly
                JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                join proteinset
                on genomicannotation.Annotation_ID=proteinset.Annotation_ID
                join blastdb
                on blastdb.Protein_ID=proteinset.Protein_ID
                WHERE assembly.Assembly_ID = {0} and assembly.assembly_version = {1};""",
                """SELECT assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, blastdb.Dir_Location
                FROM assembly
                JOIN species
                ON assembly.species=species.species_id
                JOIN genomicannotation
                ON assembly.Assembly_ID=genomicannotation.Assembly_ID AND assembly.assembly_version=genomicannotation.assembly_version
                join proteinset
                on genomicannotation.Annotation_ID=proteinset.Annotation_ID
                join blastdb
                on blastdb.Protein_ID=proteinset.Protein_ID
                WHERE Species.taxonomy LIKE "%{0}%";""",
                ]
        self.SQL_COMMANDS_LIST = [
                self.SQL_COMMANDS,
                self.SQL_COMMANDS_1,
                self.SQL_COMMANDS_2,
                self.SQL_COMMANDS_3,
                self.SQL_COMMANDS_4,
                self.SQL_COMMANDS_5,
                ]


    def add_file_type(self, my_list):
        """
            add a file type variable to the list using the last element [i][-1] extension
            For next user can use match/case python 3.10 and above"""
        MY_FILE_TYPES={
                "na": "Genome",
                "ff": "Gene Features",
                "fa": "Longest Protein",
                "aa": "All Proteins",
                "on": "Feature Annotation",
        }
        for i in range(len(my_list)):
            if "blast_dir" in my_list[i][-1]:
                my_list[i] = tuple(["Blast DB"]) + my_list[i]
            else:
                my_list[i] = tuple([MY_FILE_TYPES[ my_list[i][-1][-2:] ]]) + my_list[i]
        return my_list


    def column_maker(self):
        """
        Get the collumn to show for the mysql_results html page
        """
        return ["File type", "Assembly ID", "Assembly Version", "NCBI ID", "Specie's name", "Alias", "Assembly Source", "File Location"]


    def data_base_connection(
            self,
            db_user=DATABASES['default']['USER'],
            db_password=DATABASES['default']['PASSWORD'],
            db_host=DATABASES['default']['HOST'],
            db_database=DATABASES['default']['NAME'],
            ):
        """
        Connects to the data base
        Requirements
        _______________________________
            from mysql.connector import connect
            >>> pip install mysql-connector-python
        _______________________________
        ///////////////////////////////

        Returns
        _______________________________
        None.
        """
        try:
            self.conn = connect(user=db_user,
                                password=db_password,
                                host=db_host,
                                database=db_database,
                                autocommit=True )
            self.my_cursor = self.conn.cursor()
            print("Connected to database sucessfully")
        except Exception as error:
            print("Connection error: ", error)


    def create_shortcuts(self, path: str, target='', wDir='', icon='') -> None:
        """
        Please modifey! // https://www.blog.pythonlibrary.org/2010/01/23/using-python-to-create-shortcuts/
        Import requirements:
        from win32com.client import Dispatch

        """
        ext = path[-3:]
        if ext == 'url':
            shortcut = file(path, 'w')
            shortcut.write('[InternetShortcut]\n')
            shortcut.write('URL=%s' % target)
            shortcut.close()
        else:
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = wDir
            if icon == '':
                pass
            else:
                shortcut.IconLocation = icon
            shortcut.save()
        return


    def execute_sql_line(self, mysql_line, mysql_values = []):
        try:
            #print("Querry :", mysql_line.format(*mysql_values))
            self.my_cursor.execute(mysql_line.format(*mysql_values))
        except Exception as errors:
            ("SQL request error occured!")
            self.error_lines += [(mysql_line, mysql_values)]
            pass


    def fill_register(self, search_querry):
        """"Requires:   self.username
            fills the coreesponding user register"""
        # save the search in personal space
        print("Register called")
        Searchregister(
                user=self.user,
                querry_used=search_querry,
                ).save()
        search_instance = Searchregister.objects.last() #.search_id
        for rslt in self.search_results:
            Searchresults(
                    search_id=search_instance,
                    file_type=rslt[0],
                    assembly_id=rslt[1],
                    assembly_version=rslt[2],
                    ncbi_id=rslt[3],
                    species_name=rslt[4],
                    alias=rslt[5],
                    assembly_source=rslt[6],
                    file_location=rslt[7]
                    ).save()


    def get_my_history(self):  # DELETE ME
        self.search_history = []
        self.MY_SEARCH_COLLUMNS = ['Date', 'Querry']
        self.execute_sql_line("SELECT date_of_the_experiment, querry_used FROM djtest3.searchregister WHERE User_id={0};", [self.user.id])
        self.search_history += self.my_cursor.fetchall()
        #print("the history is:", self.search_history)
        return self.search_history


    def get_my_history_id(self):  #DELETE ME
        self.search_history_id = []
        print("user: ", self.user.id)
        self.execute_sql_line("SELECT Search_ID FROM djtest3.searchregister WHERE User_id={0};", [self.user.id])
        self.search_history_id += self.my_cursor.fetchall()
        return self.search_history_id

    def get_only_mysql_rslt_path(self):
        rslt_path = []
        for i in self.search_results:
            rslt_path.append(i[-1])

        return rslt_path

    
    def html_paginator_bar_generator(self, page_number: int, total_page_number: int, page_inter=5) -> list:
        """"creates a list of the pages to show"""
        my_html_paginator_list = [ i for i in range(max(1, page_number-page_inter//2), 
                                                    min(total_page_number, page_number+page_inter//2)+1
                                                    ) ]
        return my_html_paginator_list


    def look_for_this(self, search_querry: str, search_type: list, splitter=";") -> None:
        """
        new update can now search for a list of elements
        looks for search_querry in the database
            (P.S: database can be change in database )
        search_type :
            0: fna
            1: gff
            2, 3: fa faa (2 and 3 are the same, for the moment)
            4: json
            5: Blast dir
            6+: Not implemented yet
        _______________________________
        The results can be found in => self.search_results <=
        """
        if search_querry:
            search_list = search_querry.split(splitter)
            for search_item in search_list:
                self.search_querry = [search_item]
                for i in search_type:
                    if i not in ['0', '1', '2', '3', '4', '5']:
                        continue
                    self.execute_sql_line(
                            self.SQL_COMMANDS_LIST[int(i)][ self.what_is_my_request(search_item) ],
                            self.search_querry
                            )
                    self.search_results += self.my_cursor.fetchall()
            #print("Done looking !!! ", self.search_results)
            self.search_results.sort(key=lambda tup: tup[3])  # sort with names
            self.search_results = self.add_file_type(self.search_results)
            self.fill_register(search_querry)
        else:
            self.search_results = []  # Incase a new search is made


    def what_is_my_request(self, my_string: str) -> int:
        """ Check what is the Querry
        Input:
        ____________________________
        my_string : contains the querry
        ____________________________
        ////////////////////////////
        Returns
        ____________________________
        the type of the querry:
            - 0 ncbi_id (if it's int) =
            - 1 species_name (if it's a string)
            - 2 assembly (if it's float)
            - None
        """
        try:
            my_float = float(my_string)
            self.search_querry= my_string.split(".")
            return 0 if my_float == int(my_float) else 2

        except ValueError:
            if my_string[0] == "*":
                self.search_querry = [my_string[1:]]
                return 3
            else:
                return 1

        print("Unknown Error 6456564.")
        return None


if __name__ == "__main__":
    print("What are you doing?")
