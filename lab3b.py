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
        sys.exit(1)
total_block = int(superblock[0][1])
total_inode = int(superblock[0][2])
block_size = int(superblock[0][3])
inode_size = int(superblock[0][4])
first_none_reserved_inode = int(superblock[0][7])
INODE_FILETYPE_POS = 2
INODE_BLOCKSTART = 12
INODE_BLOCKEND = 24
INODE_INDIRECT = 24
INODE_DOUBLE_INDIRECT = 25
INODE_TRIPLE_INDIRECT = 26
INODE_NUMBER = 1
EXIT_CODE = 0
st = 0
block_appear = {i: "unknown" for i in range(st, total_block + st)}
inode_free = [ifree[i][1] for i in range(len(ifree))]
first_inode = int(group[0][8])
inode_table_size = int(math.ceil(int(int(group[0][3]) * inode_size / block_size)))  # in unit of blocks
for bf in bfree:
    block_appear[int(bf[1])] = "free"

for i in range(st, first_inode + inode_table_size):
    block_appear[i] = "reserved"

inode_link_num = {i: 0 for i in range(1, total_inode + 1)}
INODE_LINK_POSITION = 6
for i in inode:
    inode_link_num[int(i[INODE_NUMBER])] = int(i[INODE_LINK_POSITION])
    if i[INODE_NUMBER] in inode_free:
        print("ALLOCATED INODE " + i[INODE_NUMBER] + " ON FREELIST")
        EXIT_CODE = 2
    if i[INODE_FILETYPE_POS] == 'f' or i[INODE_FILETYPE_POS] == 'd' or (i[INODE_FILETYPE_POS] == 's' and len(
            i) == 27):  # symbolic link with length longer than 60 bytes should also be analyzed
        for num in range(INODE_BLOCKSTART, INODE_BLOCKEND):
            if int(i[num]) < 0 or int(i[num]) > total_block - 1:
                print("INVALID BLOCK " + i[num] + " IN INODE " + i[INODE_NUMBER] + " AT OFFSET " + str(int(
                    num - INODE_BLOCKSTART)))
                EXIT_CODE = 2

            elif int(i[num]) > 0:

                # print(block_appear[int(i[num])-1])
                if block_appear[int(i[num])] == "free":
                    print("ALLOCATED BLOCK " + i[num] + " ON FREELIST")
                    EXIT_CODE = 2
                elif block_appear[int(i[num])] == "reserved":
                    print("RESERVED BLOCK " + i[num] + " IN INODE " + i[INODE_NUMBER] + " AT OFFSET " + str(int(
                        num - INODE_BLOCKSTART)))
                    EXIT_CODE = 2
                elif block_appear[int(i[num])] == "unknown":
                    block_appear[int(i[num])] = "BLOCK " + i[num] + " IN INODE " + i[
                        INODE_NUMBER] + " AT OFFSET " + str(int(
                        num - INODE_BLOCKSTART))
                    # print(int(i[num]))
                elif block_appear[int(i[num])] == "duplicated":
                    print("DUPLICATE BLOCK " + i[num] + " IN INODE " + i[INODE_NUMBER] + " AT OFFSET " + str(int(
                        num - INODE_BLOCKSTART)))
                    EXIT_CODE = 2
                else:
                    print("DUPLICATE " + block_appear[int(i[num])])
                    print("DUPLICATE BLOCK " + i[num] + " IN INODE " + i[INODE_NUMBER] + " AT OFFSET " + str(int(
                        num - INODE_BLOCKSTART)))
                    block_appear[int(i[num])] = "duplicated"
                    EXIT_CODE = 2

        if int(i[INODE_INDIRECT]) < 0 or int(i[INODE_INDIRECT]) > total_block - 1:
            print("INVALID INDIRECT BLOCK " + i[INODE_INDIRECT] + " IN INODE " + i[INODE_NUMBER] + " AT OFFSET 12")
            EXIT_CODE = 2
        elif int(i[INODE_INDIRECT]) != 0:
            if block_appear[int(i[INODE_INDIRECT])] == "free":
                print("ALLOCATED BLOCK " + i[INODE_INDIRECT] + " ON FREELIST")
                EXIT_CODE = 2
            elif block_appear[int(i[INODE_INDIRECT])] == "reserved":
                print("RESERVED INDIRECT BLOCK " + i[INODE_INDIRECT] + " IN INODE " + i[INODE_NUMBER] + " AT OFFSET 12")
                EXIT_CODE = 2
            elif block_appear[int(i[INODE_INDIRECT])] == "unknown":
                block_appear[int(i[INODE_INDIRECT])] = "INDIRECT BLOCK " + i[INODE_INDIRECT] + " IN INODE " + i[
                    INODE_NUMBER] + " AT OFFSET 12"
            elif block_appear[int(i[INODE_INDIRECT])] == "duplicated":
                print(
                    "DUPLICATE INDIRECT BLOCK " + i[INODE_INDIRECT] + " IN INODE " + i[INODE_NUMBER] + " AT OFFSET 12")
                EXIT_CODE = 2
            else:
                print("DUPLICATE " + block_appear[int(i[INODE_INDIRECT])])
                print(
                    "DUPLICATE INDIRECT BLOCK " + i[INODE_INDIRECT] + " IN INODE " + i[INODE_NUMBER] + " AT OFFSET 12")
                block_appear[int(i[INODE_INDIRECT])] = "duplicated"
                EXIT_CODE = 2

        if int(i[INODE_DOUBLE_INDIRECT]) < 0 or int(i[INODE_DOUBLE_INDIRECT]) > total_block - 1:
            print("INVALID DOUBLE INDIRECT BLOCK " + i[INODE_DOUBLE_INDIRECT] + " IN INODE " + i[
                INODE_NUMBER] + " AT OFFSET " + str(int(12 + block_size / 4)))
            EXIT_CODE = 2
        elif int(i[INODE_DOUBLE_INDIRECT]) != 0:
            if block_appear[int(i[INODE_DOUBLE_INDIRECT])] == "free":
                print("ALLOCATED BLOCK " + i[INODE_DOUBLE_INDIRECT] + " ON FREELIST")
                EXIT_CODE = 2
            elif block_appear[int(i[INODE_DOUBLE_INDIRECT])] == "reserved":
                print("RESERVED DOUBLE INDIRECT BLOCK " + i[INODE_DOUBLE_INDIRECT] + " IN INODE " + i[
                    INODE_NUMBER] + " AT OFFSET " + str(int(12 + block_size / 4)))
                EXIT_CODE = 2
            elif block_appear[int(i[INODE_DOUBLE_INDIRECT])] == "unknown":
                block_appear[int(i[INODE_DOUBLE_INDIRECT])] = "DOUBLE INDIRECT BLOCK " + i[
                    INODE_DOUBLE_INDIRECT] + " IN INODE " + i[
                                                                  INODE_NUMBER] + " AT OFFSET " + str(
                    int(12 + block_size / 4))
            elif block_appear[int(i[INODE_DOUBLE_INDIRECT])] == "duplicated":
                print("DUPLICATE DOUBLE INDIRECT BLOCK " + i[INODE_DOUBLE_INDIRECT] + " IN INODE " + i[
                    INODE_NUMBER] + " AT OFFSET " + str(int(12 + block_size / 4)))
                EXIT_CODE = 2
            else:
                print("DUPLICATE " + block_appear[int(i[INODE_DOUBLE_INDIRECT])])
                print("DUPLICATE DOUBLE INDIRECT BLOCK " + i[INODE_DOUBLE_INDIRECT] + " IN INODE " + i[
                    INODE_NUMBER] + " AT OFFSET " + str(int(12 + block_size / 4)))
                block_appear[int(i[INODE_DOUBLE_INDIRECT])] = "duplicated"
                EXIT_CODE = 2

        if int(i[INODE_TRIPLE_INDIRECT]) < 0 or int(i[INODE_TRIPLE_INDIRECT]) > total_block - 1:
            print("INVALID TRIPLE INDIRECT BLOCK " + i[INODE_TRIPLE_INDIRECT] + " IN INODE " + i[
                INODE_NUMBER] + " AT OFFSET " + str(int(12 + block_size / 4 + (block_size / 4) ** 2)))
            EXIT_CODE = 2
        elif int(i[INODE_TRIPLE_INDIRECT]) != 0:
            if block_appear[int(i[INODE_TRIPLE_INDIRECT])] == "free":
                print("ALLOCATED BLOCK " + i[INODE_TRIPLE_INDIRECT] + " ON FREELIST")
                EXIT_CODE = 2
            elif block_appear[int(i[INODE_TRIPLE_INDIRECT])] == "reserved":
                print("RESERVED TRIPLE INDIRECT BLOCK " + i[INODE_TRIPLE_INDIRECT] + " IN INODE " + i[
                    INODE_NUMBER] + " AT OFFSET " + str(int(12 + block_size / 4 + (block_size / 4) ** 2)))
                EXIT_CODE = 2

            elif block_appear[int(i[INODE_TRIPLE_INDIRECT])] == "unknown":
                block_appear[int(i[INODE_TRIPLE_INDIRECT])] = "TRIPLE INDIRECT BLOCK " + i[
                    INODE_TRIPLE_INDIRECT] + " IN INODE " + i[
                                                                  INODE_NUMBER] + " AT OFFSET " + str(
                    int(12 + block_size / 4 + (block_size / 4) ** 2))
            elif block_appear[int(i[INODE_TRIPLE_INDIRECT])] == "duplicated":
                print("DUPLICATE TRIPLE INDIRECT BLOCK " + i[INODE_TRIPLE_INDIRECT] + " IN INODE " + i[
                    INODE_NUMBER] + " AT OFFSET " + str(int(12 + block_size / 4 + (block_size / 4) ** 2)))
                EXIT_CODE = 2
            else:
                print("DUPLICATE " + block_appear[int(i[INODE_TRIPLE_INDIRECT])])
                print("DUPLICATE TRIPLE INDIRECT BLOCK " + i[INODE_TRIPLE_INDIRECT] + " IN INODE " + i[
                    INODE_NUMBER] + " AT OFFSET " + str(int(12 + block_size / 4 + (block_size / 4) ** 2)))
                block_appear[int(i[INODE_TRIPLE_INDIRECT])] = "duplicated"
                EXIT_CODE = 2

for i in indirect:
    referenced_block_number = int(i[5])
    owning_inode = int(i[1])
    level_of_indirection = int(i[2])
    logical_block_offset = int(i[3])
    block_type = " "
    if level_of_indirection - 1 == 1:
        block_type = " INDIRECT "
    elif level_of_indirection - 1 == 2:
        block_type = " DOUBLE INDIRECT "

    if referenced_block_number < 0 or referenced_block_number > total_block - 1:
        print("INVALID" + block_type + "BLOCK " + str(referenced_block_number) + " IN INODE " + str(
            owning_inode) + " AT OFFSET " + str(logical_block_offset))
        EXIT_CODE = 2
    elif referenced_block_number > 0:
        if block_appear[referenced_block_number] == "free":
            print("ALLOCATED BLOCK " + str(referenced_block_number) + " ON FREELIST")
            EXIT_CODE = 2
        elif block_appear[referenced_block_number] == "reserved":
            print(
                "RESERVED" + block_type + "BLOCK " + str(referenced_block_number) + " IN INODE " + str(
                    owning_inode) + " AT OFFSET " + str(
                    logical_block_offset))
            EXIT_CODE = 2
        elif block_appear[referenced_block_number] == "unknown":
            block_appear[referenced_block_number] = block_type + "BLOCK " + str(
                referenced_block_number) + " IN INODE " + str(
                owning_inode) + " AT OFFSET " + str(logical_block_offset)
        elif block_appear[referenced_block_number] == "duplicated":
            print("DUPLICATE" + block_type + "BLOCK " + str(referenced_block_number) + " IN INODE " + str(
                owning_inode) + " AT OFFSET " + str(logical_block_offset))
            EXIT_CODE = 2
        else:
            print("DUPLICATE" + block_appear[referenced_block_number])
            print("DUPLICATE" + block_type + "BLOCK " + str(referenced_block_number) + " IN INODE " + str(
                owning_inode) + " AT OFFSET " + str(logical_block_offset))
            block_appear[referenced_block_number] = "duplicated"
            EXIT_CODE = 2

for i in range(first_none_reserved_inode, total_inode + 1):
    allocated = False
    for j in inode:
        if int(j[1]) == i:
            allocated = True
    on_freelist = False
    for k in ifree:
        if int(k[1]) == i:
            on_freelist = True
    if (not allocated) and (not on_freelist):
        print("UNALLOCATED INODE " + str(i) + " NOT ON FREELIST")
        EXIT_CODE = 2

invalid_and_unallocated_inodes = []
inode_appear = {i: 0 for i in range(1, total_inode + 1)}
DIRENT_INODE_POS = 3
for d in dirent:
    if int(d[3]) < 1 or int(d[3]) > total_inode:
        print("DIRECTORY INODE " + str(d[1]) + " NAME " + d[6] + " INVALID INODE " + str(d[3]))
        invalid_and_unallocated_inodes.append(d[3])
        EXIT_CODE = 2
    else:
        allocated_flag = False
        for i in inode:
            if int(i[1]) == int(d[3]):
                allocated_flag = True
        if not allocated_flag:
            print("DIRECTORY INODE " + str(d[1]) + " NAME " + d[6] + " UNALLOCATED INODE " + str(d[3]))
            invalid_and_unallocated_inodes.append(d[3])
            EXIT_CODE = 2
        else:
            inode_appear[int(d[3])] += 1

for d in dirent:
    if (d[1] != d[3]) and (d[6] == "\'.\'"):
        print("DIRECTORY INODE " + str(d[1]) + " NAME '.' LINK TO INODE " + str(d[3]) + " SHOULD BE " + str(d[1]))
        EXIT_CODE = 2

parents_and_children = {}
for d in dirent:
    if (int(d[3]) not in invalid_and_unallocated_inodes) and (d[6] != "\'.\'") and (d[6] != "\'..\'"):
        parents_and_children.update({int(d[3]): int(d[1])})  # child: parent

for d in dirent:
    if (int(d[3]) not in invalid_and_unallocated_inodes) and (d[6] == "\'..\'"):
        if int(d[1]) == 2:
            if int(d[3]) != 2:
                print("DIRECTORY INODE 2 NAME '..' LINK TO INODE " + str(d[3]) + " SHOULD BE 2")
                EXIT_CODE = 2
        else:
            if int(d[3]) != parents_and_children[int(d[1])]:
                print("DIRECTORY INODE " + str(d[1]) + " NAME '..' LINK TO INODE " + str(d[3]) + " SHOULD BE " + str(
                    parents_and_children[int(d[1])]))
                EXIT_CODE = 2

# print(block_appear)
for i in range(st, total_block + st):
    if block_appear[i] == 'unknown':
        print("UNREFERENCED BLOCK " + str(i))
        EXIT_CODE = 2
for i in range(1, total_inode + 1):
    if inode_link_num[i] != inode_appear[i]:
        print("INODE " + str(i) + " HAS " + str(inode_appear[i]) + " LINKS BUT LINKCOUNT IS " + str(inode_link_num[i]))
        EXIT_CODE = 2
sys.exit(EXIT_CODE)
