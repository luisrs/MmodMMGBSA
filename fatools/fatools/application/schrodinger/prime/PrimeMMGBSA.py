import os
import os.path
import csv
import time
import pprint
from schrodinger.job import queue, jobcontrol


aliases = {'r_psp_Rec_Strain_Energy': 'strain_protein',
           'r_psp_Lig_Strain_Energy': 'strain_ligand',
           'r_psp_MMGBSA_dG_Bind_Solv_GB': 'mmgbsa_solvation',
           'r_psp_MMGBSA_dG_Bind': 'MMGBSA_dG_Bind'}


class PrimeMMGBSA:

    def __init__(self, infile, out_cvsfile=None, radius=None):
        self.infile = infile
        self.out_cvsfile = os.path.splitext(infile)[0] + '-out.csv'

    def run_job(self):
        job = jobcontrol.launch_job(queue.get_command(
            ['prime_mmgbsa', '-flexdist', '7', self.infile], procs=4))
        while True:
            job.readAgain()
            if job.isComplete():
                break
            else:
                pass
        print "Job success PrimeMMGBSA: ", self.infile
        return job.succeeded()

    def __getitem__(self, item):
        return self.ligand[item]

    def read_outfile(self):
        print "Archivo de salida", self.out_cvsfile
        while((os.path.isfile(self.out_cvsfile)) is False):
            pass
        print "reading Prime Energy Terms..."
        time.sleep(1)
        energy_terms = self.read_energy_terms(self.out_cvsfile)
        self.set_energy_terms(energy_terms)

    def read_energy_terms(self, csv_file):
        with open(self.out_cvsfile, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            num_row = 0
            for row in spamreader:
                row = str(row)
                if(num_row is 0):
                    terms = row.split(',')
                    num_row += 1
                else:
                    values = row.split(',')
        energy_terms = dict(zip(terms, values))
        # title = dictionary["['title"].translate(None, '[\'')
        # print title
        # print dictionary['r_psp_Receptor_Coulomb']
        return energy_terms

    def set_energy_terms(self, energy_terms):
        # pprint.pprint(energy_terms)
        for term, value in energy_terms.iteritems():
            if('title' in term):
                term = term.translate(None, '[\'')
                value = value.translate(None, '[\'')
                self.set(term.lower(), value)
            if term in aliases.keys():
                self.set(aliases[term].lower(), value)

    def set(self, name, value):
        setattr(self, name, value)

# freen_energy = PrimeMMGBSA('1AQ1.mae')
# # freen_energy.run_job()
# freen_energy.read_outfile()
