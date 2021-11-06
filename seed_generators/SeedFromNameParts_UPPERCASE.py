#!/bin/env python3
################################################################################
# Description:
#  Script to generate Minecraft Seeds from given name parts
#  given name parts will be used completely uppercase
#
# Syntax:
#  python SeedFromNameParts_lowercase.py Ann Bob
#
# Copyright 2021 EtlamGit
################################################################################

import sys
import itertools


################################################################################
# check arguments
################################################################################
if (len(sys.argv) <= 1):
    print('Error: you have to call this script with several name parts as parameter.')
    exit(-1)

################################################################################
# generate name permutations
################################################################################
name_parts = sys.argv[1:]
name_list = itertools.permutations([_.upper() for _ in name_parts])

################################################################################
# loop over all name permutations
################################################################################
for name in list(name_list):
    seed = ''.join(name)
    print(seed)
