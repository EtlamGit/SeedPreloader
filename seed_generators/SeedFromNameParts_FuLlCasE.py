#!/bin/env python3
################################################################################
# Description:
#  Script to generate Minecraft Seeds from given name parts
#  given name parts will be used with any combination of lower/upper case
#
# Syntax:
#  python SeedFromNameParts_Capitals.py Ann Bob
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
name_list = itertools.permutations([_.lower() for _ in name_parts])

################################################################################
# loop over all name permutations
################################################################################
for name in list(name_list):
    base_seed = ''.join(name)
    lower_upper = ((_.lower(), _.upper()) for _ in base_seed)
    seeds = [''.join(x) for x in itertools.product(*lower_upper)]
    for seed in seeds:
        print(seed)
