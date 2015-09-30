#!/usr/bin/env python

# Given a NavisWorks XML export, a per-project clash-util dump, and a date, convert to
# { grouping: {'group': group, 'date': date, 'n_clashes': n_clashes} }

import xml.etree.ElementTree as ET
import json
import sys
from collections import defaultdict
import os

def parse_clash_util_json(util_file_str):
    data = json.loads(util_file_str) if type(util_file_str) == str else util_file_str

    level_of_z = dict([(float(v), k) for k, v in data['levels'].iteritems()]) # invert the level->z
    file_details = dict()
    for i, obj in enumerate(data['file_specs']):
        file_details[obj['name']] = dict(priority=i, discipline=obj['discipline'], owner=obj['owner'])

    return level_of_z, file_details


class SingleDayParser(object):
    def __init__(self, util_file_str):
        self.level_of_z, self.details_of_file = parse_clash_util_json(util_file_str)

    def compute_level_of_z(self, z):
        try:
            ceiling = next(x[1] for x in enumerate(sorted(self.level_of_z.keys())) if x[1] > z)
        except StopIteration:
            raise ValueError("z value %f higher than roof" % (z, ))
        return self.level_of_z[ceiling]

    # Return the filename that has highest priority
    def primary_of(self, owner_filenames):
        try:
            return min(owner_filenames, key=lambda fn: self.details_of_file[fn]['priority'])
        except KeyError as ex:
            print >>sys.stderr, "File %s not found in clash_util" % (ex, )
            raise ex

    def file_details(self, owner, subtopic):
        return self.details_of_file[owner][subtopic]

    def clashes_of(self, clash_xml, date):
        acc = defaultdict(lambda: defaultdict(int))
        doc = ET.parse(clash_xml)
        for item in doc.iterfind('batchtest/clashtests/clashtest/clashresults/clashresult'):
            z_coord = float(item.find('clashpoint/pos3f').attrib['z'])
            level = self.compute_level_of_z(z_coord)

            owning_files = [os.path.splitext(plink[2].text)[0] for plink in item.findall('clashobjects/clashobject/pathlink')]
            primary_owner = self.primary_of(owning_files)

            acc['Total clashes']['Total Number of Clashes'] += 1
            acc['Level'][level] += 1
            for owning_file in owning_files:
                acc['Owner'][self.file_details(owning_file, 'owner')] += 1
                acc['Discipline'][self.file_details(owning_file, 'discipline')] += 1
            acc['Primary owner'][self.file_details(primary_owner, 'owner')] += 1
            acc['Primary discipline'][self.file_details(primary_owner, 'discipline')] += 1

        clashes = dict()
        for grouping, group_obj in acc.iteritems():
            clashes[grouping] = [dict(group=k, date=date, n_clashes=v) for k, v in group_obj.iteritems()]
        return clashes

def main():
    try:
        clash_xml = sys.argv[1]
        date = sys.argv[2]
        clash_util = sys.argv[3]
    except:
        clash_xml = 'xml/PC-00-COMP-BBC-2.xml'
        date = '2015-09-01'
        clash_util = 'clash_util.json'

    print >>sys.stderr, 'clash_xml: %s, date: %s, clash_util: %s' % (clash_xml, date, clash_util)
    with open(clash_util) as fh:
        clash_util_str = fh.read()

    clashes = SingleDayParser(clash_util_str).clashes_of(clash_xml, date)

    print(json.dumps(clashes))


if __name__ == '__main__':
    sys.exit(main())
