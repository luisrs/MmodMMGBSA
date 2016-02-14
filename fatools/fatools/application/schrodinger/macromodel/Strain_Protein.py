from schrodinger import structure
from schrodinger.structutils import analyze
from schrodinger.application.macromodel.utils import SbcUtil
from fatools.application.schrodinger.macromodel.input import (
    EmbraceMinimizationInput, EnergyInput)

from fatools.application.schrodinger.macromodel.output import (
    InteractionEnergyResult, EnergyListingProteinResult)

from schrodinger.job import queue, jobcontrol
import csv
import os


def kj_to_kcal(value):
    return value * 0.239005736


class StrainProtein():

    def __init__(self, input_files):
        self.jobs_mbaemini, self.readfiles, self.poseviewer_files, self.outfiles = (
            self.process_files(input_files))

    def process_files(self, infiles):
        self.joblist_mbaemini = list()
        self.readfiles = list()
        self.outfiles = list()
        for f in infiles:
            self.write_mbae_files(f)
        return(self.joblist_mbaemini, self.readfiles, self.poseviewer_files, self.outfiles)

    def write_files_strain_protein(self, outfiles):
        self.jobs_energy_listing = list()
        self.outfiles_protein = list()
        with open('StrainProtein.csv', 'a+') as csvfile:
            spamwriter = csv.writer(
                csvfile, delimiter=' ',
                quotechar='|',
                quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(
                ['', 'Strain_Protein'])

        for infile in (self.outfiles):
            reader = structure.MaestroReader(infile)
            for st in reader:
                print st.title
                struc = (st.title).split("_")
                protein_atoms = analyze.evaluate_asl(st, "protein")
                protein = st.extract(protein_atoms)
                protein._setTitle(struc[0] + '_protein')
                metal_atoms = analyze.evaluate_asl(st, "metals")
                if (metal_atoms):
                    metals = st.extract(metal_atoms)
                    protein = protein.merge(metals)
                    protein._setTitle(struc[0] + '_protein')
                mae_infile = struc[0] + '_protein.mae'
                self.outfiles_protein.append(struc[0] + '_protein-out.mae')
                complex_pl = structure.MaestroWriter(mae_infile)
                complex_pl.append(protein)
                EnergyProteinComFile(mae_infile)
                # ifile = EnergyInput(use_substructure_file=True)
                # ifile.write(maefile=mae_infile)
                self.jobs_energy_listing.append(struc[0] + '_protein.com')

    def calculate_strain_protein(self):

        for infile in zip(self.readfiles, self.outfiles_protein):
            mbae_ligand = InteractionEnergyResult.from_file(infile[0])
            if(mbae_ligand):
                bound_energy_ptn = EnergyListingProteinResult.from_file(
                    infile[1])
                name_ptn_bound = bound_energy_ptn.keys()[0]
                name_ptn_unbound = mbae_ligand.keys()[0]

                print """Energy protein bound: {}\
                         Energy protein unbound: {}""".format(
                    bound_energy_ptn[name_ptn_bound].strain_protein,
                    mbae_ligand[name_ptn_unbound].strain_protein)
                strain_protein = (
                    (bound_energy_ptn[name_ptn_bound].strain_protein) - (
                        mbae_ligand[name_ptn_unbound].strain_protein))

                with open('StrainProtein.csv', 'a+') as csvfile:
                    spamwriter = csv.writer(
                        csvfile, delimiter=',',
                        quotechar='|',
                        quoting=csv.QUOTE_MINIMAL)

                    spamwriter.writerow([
                        name_ptn_bound,
                        strain_protein])
            else:
                print "problematic file: ", infile

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
            self._writeSbcFile(mae_infile)
            self._writeSbcFileProtein(mae_infile)
            ifile = EmbraceMinimizationInput()
            ifile.write(maefile=mae_infile)
            mbaemini_jobfile = struc[0] + '.in'
            self.joblist_mbaemini.append(mbaemini_jobfile)
            mbae_logfile = self.with_ext(infile=struc[0], ext='.log')
            self.readfiles.append(mbae_logfile)
            outfile = self.with_ext(infile=struc[0], ext='-out.mae')
            self.outfiles.append(outfile)

    def _writeSbcFile(self, infile):
        # radius = self.opts.shell_radius
        radius = 7
        print("Radius: %s  Second Radius: all" % (radius))
        # print("Radius: %s  Second Radius: %s" % (radius, radius * 4))
        reader = structure.StructureReader(infile)
        st = reader.next()
        largest_lig_st = reader.next()
        for lig_st in reader:
            if lig_st.atom_total > largest_lig_st.atom_total:
                largest_lig_st = lig_st
        st = st.merge(largest_lig_st)

        binding_site_atoms = analyze.evaluate_asl(
            st, "fillres (all and within %s ligand) and not ligand" % radius)
        nearby_atoms = analyze.evaluate_asl(
            st, "not (ligand or fillres (all and within %s ligand))" % (radius))
        # nearby_atoms = analyze.evaluate_asl(
        #     st, "not (ligand or fillres (all and within %s ligand)) and fillres within %s ligand" % (radius, radius*4))
        name_file = infile.split('.')
        sbc_file = name_file[0] + '.sbc'
        sbu = SbcUtil()
        sbu_args = [sbc_file]
        sbu_args.extend(sbu.setSubs(binding_site_atoms))
        sbu_args.extend(sbu.setFixed(nearby_atoms))
        sbu.writeSbcFile(sbu_args)

    def _writeSbcFileProtein(self, infile):
        # radius = self.opts.shell_radius
        radius = 7
        print("Radius: %s  Second Radius: all" % (radius))
        # print("Radius: %s  Second Radius: %s" % (radius, radius * 4))
        reader = structure.StructureReader(infile)
        st = reader.next()
        largest_lig_st = reader.next()
        for lig_st in reader:
            if lig_st.atom_total > largest_lig_st.atom_total:
                largest_lig_st = lig_st
        st = st.merge(largest_lig_st)

        binding_site_atoms = analyze.evaluate_asl(
            st, "fillres (all and within %s ligand) and not ligand" % radius)
        nearby_atoms = analyze.evaluate_asl(
            st, "not (ligand or fillres (all and within %s ligand))" % (radius))
        # nearby_atoms = analyze.evaluate_asl(
        #     st, "not (ligand or fillres (all and within %s ligand)) and fillres within %s ligand" % (radius, radius*4))
        name_file = infile.split('.')
        sbc_file = name_file[0] + '_protein.sbc'
        sbu = SbcUtil()
        sbu_args = [sbc_file]
        sbu_args.extend(sbu.setSubs(binding_site_atoms))
        sbu_args.extend(sbu.setFixed(nearby_atoms))
        sbu.writeSbcFile(sbu_args)

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


class EnergyProteinComFile(object):

    def __init__(self, infile):
        outfile = os.path.splitext(infile)[0] + '-out.mae'
        sbc_file = os.path.splitext(infile)[0] + '.com'
        print type(infile), outfile, sbc_file
        op_codes = """\
infile
outfile
 DEBG     601      0      0      0     0.0000     0.0000     0.0000     0.0000
 SOLV       3      1      0      0     0.0000     0.0000     0.0000     0.0000
 EXNB       0      5      0      0     8.0000    20.0000     4.0000     8.0000
 BDCO       0      0      0      0    89.4427 99999.0000     0.0000     0.0000
 FFLD      14      1      0      0     1.0000     0.0000     0.0000     0.0000
 SUBS       0      0      0      0     0.0000     0.0000     0.0000     0.0000
 BGIN       0      0      0      0     0.0000     0.0000     0.0000     0.0000
 READ       0      0      0      0     0.0000     0.0000     0.0000     0.0000
 ELST       2      0      0      0     0.0000     0.0000     0.0000     0.0000
 WRIT       0      0      0      0     0.0000     0.0000     0.0000     0.0000
 END        0      0      0      0     0.0000     0.0000     0.0000     0.0000"""
        print type(op_codes)

        op_codes = op_codes.replace("infile", str(infile))
        op_codes = op_codes.replace("outfile", str(outfile))
        fo = open(sbc_file, "wb")
        fo.write(op_codes)
        fo.close()

# objeto = EnergyProteinComFile('1AQ1_protein.mae')
