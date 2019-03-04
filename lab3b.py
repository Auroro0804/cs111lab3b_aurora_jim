# block consistency audit
# An INVALID block is one whose number is less than zero
# or greater than the highest block in the file system.

# A RESERVED block is one that could not legally be allocated to any file
# because it should be reserved for file system metadata

# INVALID BLOCK 101 IN INODE 13 AT OFFSET 0
# INVALID INDIRECT BLOCK 101 IN INODE 13 AT OFFSET 12
# INVALID DOUBLE INDIRECT BLOCK 101 IN INODE 13 AT OFFSET 268
# INVALID TRIPLE INDIRECT BLOCK 101 IN INODE 13 AT OFFSET 65804
# RESERVED INDIRECT BLOCK 3 IN INODE 13 AT OFFSET 12
# RESERVED DOUBLE INDIRECT BLOCK 3 IN INODE 13 AT OFFSET 268
# RESERVED TRIPLE INDIRECT BLOCK 3 IN INODE 13 AT OFFSET 65804
# RESERVED BLOCK 3 IN INODE 13 AT OFFSET 0

# If a block is not referenced by any file and is not on the free list,
# a message like the following should be generated to stdout:
# UNREFERENCED BLOCK 37

# A block that is allocated to some file might also appear on the free list.
# In this case a message like the following should be generated to stdout:
# ALLOCATED BLOCK 8 ON FREELIST

# If a legal block is referenced by multiple files (or even multiple times in a single file),
# messages like the following (depending on precisely where the references are) should be generated to stdout
# for each reference to that block:
# DUPLICATE BLOCK 8 IN INODE 13 AT OFFSET 0
# DUPLICATE INDIRECT BLOCK 8 IN INODE 13 AT OFFSET 12
# DUPLICATE DOUBLE INDIRECT BLOCK 8 IN INODE 13 AT OFFSET 268
# DUPLICATE TRIPLE INDIRECT BLOCK 8 IN INODE 13 AT OFFSET 65804


# inode allocation audit 
# Compare your list of allocated/unallocated I-nodes with the free I-node bitmaps,
# and for each discovered inconsistency, a message like one of the following should be generated to stdout:
# ALLOCATED INODE 2 ON FREELIST
# UNALLOCATED INODE 17 NOT ON FREELIST

# directory consistency audit

# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument("filename", help="enter the csv file containing fs info that you want to analyze.")
# args = parser.parse_args()
from __future__ import print_function

import sys
import csv
import os
import math


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# check the number of arguments passed in
if len(sys.argv) == 1:
    eprint("missing argument for file name.")
    eprint("Example: python3 lab3b.py test.csv")
    sys.exit(1)
elif len(sys.argv) > 2:
    eprint("Too many arguments passed in.")
    eprint("Example: python3 lab3b.py test.csv")
    sys.exit(1)
# check the right file type
filename = sys.argv[1]
if filename.split(".")[-1] != "csv":
    eprint("please pass in a csv file")
    sys.exit(1)
try:
    with open(filename, 'r') as f:
        try:
            reader = csv.reader(f)
            fs_info = list(reader)
        except Exception as e:
            eprint("csv reader error")
            sys.exit(1)
except IOError as e:
    eprint("I/O error({0}): {1}".format(e.errno, e.strerror))
    sys.exit(1)

superblock = []
group = []
bfree = []
ifree = []
dirent = []
inode = []
indirect = []
wrong_entry = []
for f in fs_info:
    if f[0] == "SUPERBLOCK":
        superblock.append(f)
    elif f[0] == "GROUP":
        group.append(f)
    elif f[0] == "BFREE":
        bfree.append(f)
    elif f[0] == "IFREE":
        ifree.append(f)
    elif f[0] == "DIRENT":
        dirent.append(f)
    elif f[0] == "INODE":
        inode.append(f)
    elif f[0] == "INDIRECT":
        indirect.append(f)
    else:
        eprint("WRONG ENTRY")
        wrong_entry.append(f)
total_block = int(superblock[0][1])
total_inode = int(superblock[0][2])
block_size  = int(superblock[0][3])
inode_size  = int(superblock[0][4])
INODE_FILETYPE_POS = 2
INODE_BLOCKSTART = 12
INODE_BLOCKEND = 24
INODE_INDIRECT = 24
INODE_DOUBLE_INDIRECT = 25
INODE_TRIPLE_INDIRECT = 26
INODE_NUMBER = 1
EXIT_CODE = 0
# reserved_block = [3]
st=0
if block_size>1024:
    st=0
else:
    st=1
block_appear={i:"unknown" for i in range(st, total_block + st) }
# print(block_appear)
#block_appear = [{i: "unknown"} for i in range(st, total_block + st)]
first_inode = int(group[0][8])
inode_table_size = int(math.ceil(int(int(group[0][3]) * inode_size / block_size)))  # in unit of blocks
# for i in range
# how to calculate offset
# which blocks are reserved ?
print("first_inode",first_inode)
print("inode_table_size",inode_table_size)
for bf in bfree:
    block_appear[int(bf[1])] = "free"
for i in range(st, first_inode+inode_table_size):
    block_appear[i]="reserved"

# print(block_appear)
# print(inode)
for i in inode:
    if i[INODE_FILETYPE_POS] == 'f' or i[INODE_FILETYPE_POS] == 'd':
        for num in range(INODE_BLOCKSTART, INODE_BLOCKEND):
            if int(i[num]) < 0 or int(i[num]) > total_block:
                print("INVALID BLOCK " + i[num] + " IN INODE " + i[INODE_NUMBER] + " AT OFFSET " + str(int(
                    num - INODE_BLOCKSTART)))
                EXIT_CODE = 2

            elif int(i[num]) > 0:

                # print(block_appear[int(i[num])-1])
                if block_appear[int(i[num])] == "free":
                    print("ALLOCATED BLOCK " + i[num] + " ON FREELIST")
                    EXIT_CODE = 2
                elif block_appear[int(i[num])]=="reserved":
                    print("RESERVED BLOCK " + i[num] + " IN INODE " + i[INODE_NUMBER] + " AT OFFSET " + str(int(
                    num - INODE_BLOCKSTART)))
                    EXIT_CODE = 2
                else:
                    block_appear[int(i[num])] = "file"
                    print(int(i[num]))



        if int(i[INODE_INDIRECT]) < 0 or int(i[INODE_INDIRECT]) > total_block:
            print("INVALID INDIRECT BLOCK " + i[INODE_INDIRECT] + " IN INODE " + i[INODE_NUMBER] + " AT OFFSET 12")
            EXIT_CODE = 2
        elif int(i[INODE_INDIRECT]) != 0:
            if block_appear[int(i[INODE_INDIRECT])] == "free":
                print("ALLOCATED BLOCK " + i[INODE_INDIRECT] + " ON FREELIST")
                EXIT_CODE = 2
            elif block_appear[int(i[INODE_INDIRECT])]=="reserved":
                print("RESERVED INDIRECT BLOCK " + i[INODE_INDIRECT] + " IN INODE " + i[INODE_NUMBER] + " AT OFFSET 12")
                EXIT_CODE = 2
            else:
                block_appear[int(i[INODE_INDIRECT])] = "file"


        if int(i[INODE_DOUBLE_INDIRECT]) < 0 or int(i[INODE_DOUBLE_INDIRECT]) > total_block:
            print("INVALID DOUBLE INDIRECT BLOCK " + i[INODE_DOUBLE_INDIRECT] + " IN INODE " + i[
                INODE_NUMBER] + " AT OFFSET " + str(int(12+block_size/4)))
            EXIT_CODE = 2
        elif int(i[INODE_DOUBLE_INDIRECT]) != 0:
            if block_appear[int(i[INODE_DOUBLE_INDIRECT])] == "free":
                print("ALLOCATED BLOCK " + i[INODE_DOUBLE_INDIRECT] + " ON FREELIST")
                EXIT_CODE = 2
            elif block_appear[int(i[INODE_DOUBLE_INDIRECT])]=="reserved":
                print("RESERVED DOUBLE INDIRECT BLOCK " + i[INODE_DOUBLE_INDIRECT] + " IN INODE " + i[
                    INODE_NUMBER] + " AT OFFSET " + str(int(12+block_size/4)))
                EXIT_CODE = 2 
            else:
                block_appear[int(i[INODE_DOUBLE_INDIRECT])] = "file"
        

        if int(i[INODE_TRIPLE_INDIRECT]) < 0 or int(i[INODE_TRIPLE_INDIRECT]) > total_block:
            print("INVALID TRIPLE INDIRECT BLOCK " + i[INODE_TRIPLE_INDIRECT] + " IN INODE " + i[
                INODE_NUMBER] + " AT OFFSET " + str(int(12+block_size/4+(block_size/4)**2)))
            EXIT_CODE = 2
        elif int(i[INODE_TRIPLE_INDIRECT]) != 0:
            if block_appear[int(i[INODE_TRIPLE_INDIRECT])] == "free":
                print("ALLOCATED BLOCK " + i[INODE_TRIPLE_INDIRECT] + " ON FREELIST")
                EXIT_CODE = 2
            elif block_appear[int(i[INODE_TRIPLE_INDIRECT])]=="reserved":
                print("RESERVED TRIPLE INDIRECT BLOCK " + i[INODE_TRIPLE_INDIRECT] + " IN INODE " + i[
                    INODE_NUMBER] + " AT OFFSET " + str(int(12+block_size/4+(block_size/4)**2)))
                EXIT_CODE = 2
            else:
                block_appear[int(i[INODE_TRIPLE_INDIRECT])] = "file"
        

        # if int(i[INODE_INDIRECT]) in reserved_block:
        #     print("RESERVED INDIRECT BLOCK " + i[INODE_INDIRECT] + " IN INODE " + i[INODE_NUMBER] + " AT OFFSET 12")
        #     EXIT_CODE = 2
        # if int(i[INODE_DOUBLE_INDIRECT]) in reserved_block:
        #     print("RESERVED DOUBLE INDIRECT BLOCK " + i[INODE_DOUBLE_INDIRECT] + " IN INODE " + i[
        #         INODE_NUMBER] + " AT OFFSET " + str(int(12+block_size/4)))
        #     EXIT_CODE = 2
        # if int(i[INODE_TRIPLE_INDIRECT]) in reserved_block:
        #     print("RESERVED TRIPLE INDIRECT BLOCK " + i[INODE_TRIPLE_INDIRECT] + " IN INODE " + i[
        #         INODE_NUMBER] + " AT OFFSET " + str(int(12+block_size/4+(block_size/4)**2)))
        #     EXIT_CODE = 2
print(block_appear)
for i in range(st, total_block + st):
    if block_appear[i] == 'unknown':
        print("UNREFERENCED BLOCK " + str(i))
        EXIT_CODE = 2
sys.exit(EXIT_CODE)
