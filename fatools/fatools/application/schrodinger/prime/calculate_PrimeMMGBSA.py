# import sys
# sys.path.append('/home/luis/Desktop/FranciscoAdasme/fatools')
# from fatools.application.schrodinger.macromodel.Scripts.RRHO import (
# RRHOEntropy)
from PrimeMMGBSA import PrimeMMGBSA
import glob
import os
import csv


poseviewer_files = list()
directory = os.getcwd()
# os.chdir("/home/luis/Desktop/FranciscoAdasme/fatools/fatools/application/schrodinger/macromodel/Scripts")
os.chdir(directory)
for file in glob.glob("*.mae"):
    poseviewer_files.append(file)
poseviewer_files.sort()
print("poseviewer_files : ", poseviewer_files)


def write_csvfile(title, strain_protein, strain_ligand, mmgbsa_solvation):
    with open('PrimeMMGBSA_scoring_terms.csv', 'a+') as csvfile:
        spamwriter = csv.writer(
            csvfile, delimiter=' ',
            quotechar='|',
            quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow([title, strain_protein, strain_ligand, mmgbsa_solvation])


def write_csvfile_title():
    with open('PrimeMMGBSA_scoring_terms.csv', 'w') as csvfile:
        spamwriter = csv.writer(
            csvfile, delimiter=' ',
            quotechar='|',
            quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(
            ['title', 'strain_protein', 'strain_ligand', 'mmgbsa_solvation'])

write_csvfile_title()
for f in poseviewer_files:
    print f
    prime = PrimeMMGBSA(f)
    prime.run_job()
    prime.read_outfile()
    print('Title: ', prime.title)
    write_csvfile(
        prime.title, prime.strain_protein, prime.strain_ligand, prime.mmgbsa_solvation)
print('All jobs complete [Ok]')
