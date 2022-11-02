# -*- coding: utf-8 -*-
"""
creates  file with all files 
@author: Amine
"""
from os import walk
from os.path import join


def hyperbrowser(my_location):
    with open('all_files_list.txt', 'w') as new_file:
        for line in list(walk(my_location)):
            for file_name in line[2]:
                new_file.write(join(line[0] , file_name) + "\n")
            
if __name__ == "__main__":
    hyperbrowser(input("Give path please: "))
    print( "Done!")