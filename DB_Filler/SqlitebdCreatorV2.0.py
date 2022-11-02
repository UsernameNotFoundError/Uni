# -*- coding: utf-8 -*-
"""

Creates a local mySQL DataBase using sql-file
---------
-Imports-
---------
sqlit3

@author: Amine
"""
import mysql.connector


def main(file_path = "SQL_commands_for_db_creation_10_06.sql"):
    """
    Just fills in the sql table
    :param table_to_fill:
    :return: None
    """        
    try:
        with open(file_path) as my_sqlfile:
            sql_commands = my_sqlfile.read()
    except Exception as e1:
        print("Error occured while reading file,", e1)
    conn = mysql.connector.connect(user='root',
                                   password='0000',
                                   host='localhost'
                                   )
    my_cursor = conn.cursor()
    for i in sql_commands.strip('\n').split(";")[:-1]:
        my_cursor.execute(i+";")
        #print("=======>", i+";")
    # my_cursor.execute(sql_commands.strip('\n'), multi=True)
    conn.commit()
    print("Data Base created!")
    
if __name__ == "__main__":
    main()