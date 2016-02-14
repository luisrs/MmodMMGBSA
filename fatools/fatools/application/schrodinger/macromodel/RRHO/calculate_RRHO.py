import sys
sys.path.append('/home/luis/Desktop/FranciscoAdasme/fatools')
from fatools.application.schrodinger.macromodel.Scripts.RRHO import (
    RRHOEntropy)

import glob
import os
import csv

poseviewer_files = list()
os.chdir("/home/luis/Desktop/FranciscoAdasme/fatools/fatools/application/schrodinger/macromodel/RRHO")
for file in glob.glob("*.mae"):
    poseviewer_files.append(file)

print(poseviewer_files)


def write_csvfile(title, tds_trans, tds_rot, tds_vib, tds_total):
    with open('RRHO_scoring_terms.csv', 'a+') as csvfile:
        spamwriter = csv.writer(
            csvfile, delimiter=' ',
            quotechar='|',
            quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow([title, tds_trans, tds_rot, tds_vib, tds_total])


def write_csvfile_title():
    with open('RRHO_scoring_terms.csv', 'w') as csvfile:
        spamwriter = csv.writer(
            csvfile, delimiter=' ',
            quotechar='|',
            quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['title', 'tds_trans', 'tds_rot', 'tds_vib', 'tds_total'])

for f in poseviewer_files:
    rrho = RRHOEntropy(f)
    rrho.run()
    rrho.read_outfile()
    print(rrho.title, rrho.tds_trans)
    write_csvfile_title()
    write_csvfile(rrho.title, rrho.tds_trans, rrho.tds_rot, rrho.tds_vib, rrho.tds_total)
