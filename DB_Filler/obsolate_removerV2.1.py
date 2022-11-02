# -*- coding: utf-8 -*-
"""

@author: Amine
"""

def read_file(my_location):
    with open('all_files_list.txt', 'r') as old_file:
        with open('pureged_all_files.txt', 'w') as new_file:
            for line in old_file:
                if line.find('Obsolete')<0:
                    if line.find('retired')<0:
                        if line.find('/tmp/')<0:
                            if line.find('/gffread/')<0:
                                if line.find('_backup/')<0:
                                    new_file.write(line)
                    
read_file("")
print('Done')