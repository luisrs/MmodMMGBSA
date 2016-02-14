from subprocess import call
import os
import os.path
import csv
import time


class RRHOEntropy:

    def __init__(self, infile, out_cvsfile=None, radius=None):
        if(out_cvsfile is None):
            self.out_cvsfile = os.path.splitext(infile)[0] + '_entropyRRHO.csv'
        self.command = "$SCHRODINGER/run rrho_entropy.py {} -csv {}".format(
            infile, self.out_cvsfile)
        if(radius is not None):
            r = " -r {}".format(str(radius))
            self.command = self.command + r
        print('Command: ', self.command)

    def run(self):
        print('run...')
        call(self.command, shell=True)

    def __getitem__(self, item):
        return self.ligand[item]

    def read_outfile(self):
        while((os.path.isfile(self.out_cvsfile)) is False):
            pass
        print('Reading entropy terms...')
        time.sleep(1)
        energy_terms = self.read_entropy_terms(self.out_cvsfile)
        self.set_energy_terms(energy_terms)

    def read_entropy_terms(self, csv_file):
        row_list = list()
        with open(self.out_cvsfile, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in spamreader:
                row_list.append(row[0].split(','))
        row1 = row_list[0]
        row2 = row_list[1]
        energy_terms = dict(zip(row1, row2))
        # print(energy_terms['TdS_total'])
        return energy_terms

    def set_energy_terms(self, energy_terms):
        for term, value in energy_terms.iteritems():
            self.set(term.lower(), value)

    def set(self, name, value):
        setattr(self, name, value)

# objeto = RRHOEntropy('2EXM.mae')
# objeto.read_outfile()
# print(objeto.tds_trans)
