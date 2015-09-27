#!/usr/bin/env python

# Given a days of 
#  { grouping: {'group': group, 'date': date, 'n_clashes': n_clashes} }
# Compile into a single object

import json
import sys
from collections import defaultdict

acc = defaultdict(list)
for day_json_file in sys.argv[1:]:
    with open(day_json_file) as fh:
        for (grouping, group_tuples) in json.load(fh).iteritems():
            acc[grouping].extend(group_tuples)

print(json.dumps(acc))
