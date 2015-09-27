#!/usr/bin/env python

# Given a NavisWorks XML export, a per-project clash-util dump, and a date, convert to 
# { grouping: {'group': group, 'date': date, 'n_clashes': n_clashes} }

import xml.etree.ElementTree as ET
import json
import sys
from collections import defaultdict

def parse_clash_util_json(util_file):
    with open(util_file) as fh:
        data = json.load(fh)
    return (
        dict([(float(v), k) for (k, v) in data['levels'].iteritems()]), 
        data['file_key'], 
        data['responsibility']
    )

def compute_level_of_z(z):
    try:
        ceiling = next(x[1] for x in enumerate(sorted(level_of_z.keys())) if x[1] > z)
    except StopIteration:
        raise ValueError("z value %f higher than roof" % z)
    return level_of_z[ceiling]

# Two owners if they're from the same discipline
# Else a list of one owner based on whose discipline has priority
def primary_of(owner_objs):
    try:
        if owner_objs[0]['discipline'] == owner_objs[1]['discipline']:
            return owner_objs
    except KeyError as ex:
        raise ValueError("sub %s not found in responsibility hierarchy" % ex)
    return [ min(owner_objs, key=lambda obj: responsibility.index(obj['discipline'])) ]

def accumulate_clashes(clash_xml):
    acc = defaultdict(lambda : defaultdict(int))
    doc = ET.parse(clash_xml)
    for item in doc.iterfind('batchtest/clashtests/clashtest/clashresults/clashresult'):
        z = float(item.find('clashpoint/pos3f').attrib['z'])
        level = compute_level_of_z(z)

        owning_files = [plink[2].text for plink in item.findall('clashobjects/clashobject/pathlink')]
        try:
            disciplines = [owner_of_file[f]['discipline'] for f in owning_files]
            owners =      [owner_of_file[f]['owner'] for f in owning_files]
            primaries = primary_of([owner_of_file[f] for f in owning_files])
            primary_disciplines = [p['discipline'] for p in primaries]
            primary_owners =      [p['owner'] for p in primaries]
        except KeyError as ex:
            raise ValueError("File %s not found in clash_util" % ex)

        acc['level'][level] += 1
        for owner in owners:
            acc['owner'][owner] += 1
        for discipline in disciplines:
            acc['discipline'][discipline] += 1
        for primary_owner in primary_owners:
            acc['primary_owner'][owner] += 1
        for primary_discipline in primary_disciplines:
            acc['primary_discipline'][discipline] += 1

    return acc

try:
    clash_xml = sys.argv[1]
    date = sys.argv[2]
    clash_util = sys.argv[3]
except:
    clash_xml = 'xml/PC-00-COMP-BBC-2.xml'
    date = '2015-09-01'
    clash_util = 'clash_util.json'

(level_of_z, owner_of_file, responsibility) = parse_clash_util_json(clash_util)
summed_clashes_of = accumulate_clashes(clash_xml)

clashes = dict()
for (grouping, group_obj) in summed_clashes_of.iteritems():
    clashes[grouping] = [{'group': k, 'date': date, 'n_clashes': v} for (k,v) in group_obj.iteritems()]

print(json.dumps(clashes))
