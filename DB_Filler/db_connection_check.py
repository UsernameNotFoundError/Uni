# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 01:18:15 2021

@author: Amine
"""

from mysql.connector import connect


def data_base_connection():
    """
    Connects to the data base 

    Returns
    -------
    None.

    """
    try:
        conn = connect(user='amine',
                            password='ChangeMe1234',
                            host='172.17.100.3',
                            database= "arche"
                               )
        print("Connected sucessfully")
        my_cursor = conn.cursor()
        conn.autocommit = True
        my_cursor.execute("show tables;")
        print(my_cursor.fetchall()[0])
        
    except:
        print("Connection error")
        
data_base_connection()