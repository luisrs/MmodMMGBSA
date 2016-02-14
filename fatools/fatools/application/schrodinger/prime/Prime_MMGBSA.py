from schrodinger import structure
from schrodinger.structutils import analyze
from schrodinger.job import queue, jobcontrol
import csv

aliases = {'r_psp_Rec_Strain_Energy': 'strain_protein',
           'r_psp_Lig_Strain_Energy': 'strain_ligand',
           'r_psp_MMGBSA_dG_Bind_Solv_GB': 'mmgbsa_solvation',
           'r_psp_MMGBSA_dG_Bind': 'MMGBSA_dG_Bind'}


def kj_to_kcal(value):
    return value * 0.239005736


class PrimeMMGBSA():

    def __init__(self, input_files):
        self.jobs_mbaemini, self.readfiles, self.poseviewer_files = (
            self.process_files(input_files))

    def process_files(self, infiles):
        self.pv_files = list()
        self.joblist_confsearch = list()
        self.readfiles = list()
        for f in infiles:
            self.write_mbae_files(f)
        return(self.pv_files, self.readfiles, self.poseviewer_files)

    def calculate_energy_terms(self, readfile_list):
        self.write_csvfile_title()
        for outfile in readfile_list:
            energy_terms = self.read_energy_terms(outfile)
            self.set_energy_terms(energy_terms)
            self.write_csvfile(
                self.title, self.strain_protein, self.strain_ligand,
                self.mmgbsa_solvation)

    def read_energy_terms(self, csv_file):
        with open(csv_file, 'rb') as csvfile:
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

    def with_ext(self, infile=None, ext=None):
        if '.' in infile:
            name_file = infile.split('.')[0]
            return name_file + ext
        else:
            return infile + ext

    def write_mbae_files(self, infile):
        self.poseviewer_files = list()
        reader = structure.StructureReader(infile)
        for st in reader:
            struc = (st.title).split("_")
            protein_atoms = analyze.evaluate_asl(st, "protein")
            protein = st.extract(protein_atoms)
            protein._setTitle(struc[0] + '_protein')
            metal_atoms = analyze.evaluate_asl(st, "metals")
            if (metal_atoms):
                metals = st.extract(metal_atoms)
                protein = protein.merge(metals)
                protein._setTitle(struc[0] + '_protein')
            indices = analyze.evaluate_asl(st, '(ligand)')
            ligand = st.extract(indices, True)
            ligand._setTitle(struc[0] + '_ligand')
            mae_infile = struc[0] + '.mae'
            complex_pl = structure.MaestroWriter(mae_infile)
            complex_pl.append(protein)
            complex_pl.append(ligand)
            self.poseviewer_files.append(mae_infile)
            csvfile = self.with_ext(infile=struc[0], ext='-out.csv')
            self.readfiles.append(csvfile)
            self.pv_files.append(mae_infile)

    def _launchComFile(self, jobfile):
        job = jobcontrol.launch_job(queue.get_command(
            ['macromodel', jobfile], procs=4))
        while True:
            job.readAgain()
            if job.isComplete():
                break
            else:
                pass
        return job.succeeded()

    def write_csvfile_title(self):
        with open('PrimeMMGBSA_scoring_terms.csv', 'w') as csvfile:
            spamwriter = csv.writer(
                csvfile, delimiter=' ',
                quotechar='|',
                quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(
                ['title', 'strain_protein', 'strain_ligand', 'mmgbsa_solvation'])

    def write_csvfile(self, title, strain_protein, strain_ligand, mmgbsa_solvation):
        with open('PrimeMMGBSA_scoring_terms.csv', 'a+') as csvfile:
            spamwriter = csv.writer(
                csvfile, delimiter=' ',
                quotechar='|',
                quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([title, strain_protein, strain_ligand, mmgbsa_solvation])
