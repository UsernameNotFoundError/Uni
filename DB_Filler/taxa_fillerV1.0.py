# -*- coding: utf-8 -*-
"""
script to fill taxa collumn
Created on Wed Feb  9

@author: Amine
"""
from mysql.connector import connect, Error
from sys import argv


def main(taxa_file_path=argv[1]):
    print("file path is:", taxa_file_path)
    database_name="Genomes"
    conn = connect(user='amine',
            password='ChangeMe1234',
            host='172.17.100.21',
            database=database_name
            )
    my_cursor = conn.cursor(buffered=True)
    my_cursor.execute("Use "+ database_name + ";")
    conn.autocommit = True
    print("Connected sucessfully")
    my_cursor.execute("ALTER TABLE Species MODIFY COLUMN taxonomy VARCHAR(1000);")
    with open(taxa_file_path, 'r') as taxa_file:
        for line in taxa_file:
            my_taxa_data = line[:-1].split(";")
            if 'GCF' in my_taxa_data[-3]:
                my_cursor.execute(
                        """UPDATE Species SET taxonomy="{0}" WHERE Species_Name="{1}";""".format(
                                *[";".join(my_taxa_data[:-5]), my_taxa_data[-4]]
                                )
                        )  # Fill taxa in species table
            else:
                my_cursor.execute(
                        """UPDATE Species SET taxonomy="{0}" WHERE Species_Name="{1}";""".format(
                                *[";".join(my_taxa_data[:-6]), my_taxa_data[-5]]
                                ) 
                        )  # Fill taxa in species table


if __name__=="__main__":
    main()