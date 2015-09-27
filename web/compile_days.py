#!/usr/bin/env python

# Given a days of
#  { grouping: {'group': group, 'date': date, 'n_clashes': n_clashes} }
# Compile into a single object

import json
import sys
from collections import defaultdict


def combine_readers(readers):
    acc = defaultdict(list)
    for reader in readers:
        for grouping, group_tuples in json.load(reader).iteritems():
            acc[grouping].extend(group_tuples)
    return acc


def combine_files(file_names):
    return combine_readers((open(_) for _ in file_names))


def main():
    acc = combine_files(sys.argv[1:])
    print(json.dumps(acc))


if __name__ == '__main__':
    sys.exit(main())
