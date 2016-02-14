from schrodinger import structure
from schrodinger.structutils import analyze
from schrodinger.application.macromodel.utils import SbcUtil
from fatools.application.schrodinger.macromodel.input import (
    ConfSearchInput, EmbraceMinimizationInput, EnergyInput, RRHOEntropy)

from fatools.application.schrodinger.macromodel.output import (
    EnergyListingResult, InteractionEnergyResult)

from schrodinger.utils import fileutils
from schrodinger.job import queue, jobcontrol
import csv


def kj_to_kcal(value):
    return value * 0.239005736


class MmodMMGBSA():

    def __init__(self, input_files, radius):
        self.radius = radius
        self.jobs_mbaemini, self.jobs_confsearch, self.readfiles, self.poseviewer_files = (
            self.process_files(input_files))

    def process_files(self, infiles):
        self.joblist_mbaemini = list()
        self.joblist_confsearch = list()
        self.readfiles = list()
        for f in infiles:
            self.write_confsearch_files(f)
            self.write_mbae_files(f)
        return(self.joblist_mbaemini, self.joblist_confsearch, self.readfiles, self.poseviewer_files)

    def calculate_entropyRRHO(self):
        for poseviewer in self.poseviewer_files:
            print(poseviewer)
            entropy = RRHOEntropy(poseviewer)
            entropy.run()
            entropy.read_outfiles()

    def calculate_scoring_function(self, readfile_list):
        job_energy = self._launchComFile(self.energy_listing)
        if(job_energy):
            mbae_result = list()
            cvs_outfile = str(self.radius)+'Flex_RestoFijo.csv'
            with open(cvs_outfile, 'a+') as csvfile:
                spamwriter = csv.writer(
                    csvfile, delimiter=' ',
                    quotechar='|',
                    quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow(
                    ['', 'Evdw', 'Eelect', 'SOLVunbound', 'SOLVbound', 'dGsolv',
                        'Eintra_unbound', 'Eintra_bound', 'dEintra',
                        'Entropy', 'Eptn'])
            for infile in readfile_list:
                if fileutils.is_maestro_file(infile):
                    energy_listing = EnergyListingResult.from_file(infile)
                else:
                    mbae_ligand = InteractionEnergyResult.from_file(infile)
                    if(mbae_ligand):
                        mbae_result.append(mbae_ligand)
                    else:
                        print "problematic file: ", infile
            for mbaemini in mbae_result:
                ligand = mbaemini.keys()[0]
                if(energy_listing[ligand] is None):
                    pass
                else:
                    dg_solv = mbaemini[ligand].solv_bound - energy_listing[ligand].solv_unbound
                    dg_intra = mbaemini[ligand].intra_bound - energy_listing[ligand].intra_unbound

                    with open(cvs_outfile, 'a+') as csvfile:
                        spamwriter = csv.writer(
                            csvfile, delimiter=',',
                            quotechar='|',
                            quoting=csv.QUOTE_MINIMAL)

                        spamwriter.writerow([
                            ligand,
                            mbaemini[ligand].vdw,
                            mbaemini[ligand].electrostatic,
                            energy_listing[ligand].solv_unbound,
                            mbaemini[ligand].solv_bound,
                            dg_solv,
                            energy_listing[ligand].intra_unbound,
                            mbaemini[ligand].intra_bound,
                            dg_intra,
                            energy_listing[ligand].entropy,
                            mbaemini[ligand].strain_protein])
            return True

    def with_ext(self, infile=None, ext=None):
        if '.' in infile:
            name_file = infile.split('.')[0]
            return name_file + ext
        else:
            return infile + ext

    def write_confsearch_files(self, infile):

        csearch_file = self.with_ext(infile=infile, ext='_confsearch.mae')
        self.ligands = csearch_file
        writer = structure.StructureWriter(csearch_file)
        reader = structure.StructureReader(infile)
        for st in reader:
            title = st.title
            name = title.split('_')[0]
            indices = analyze.evaluate_asl(st, '(ligand)')
            ligand = st.extract(indices, True)
            ligand._setTitle(name + '_ligand')
            writer.append(ligand)
        writer.close()
        ifile = ConfSearchInput(use_substructure_file=False)
        ifile.write(maefile=csearch_file)

        csearch_outfile = self.with_ext(infile=infile, ext='_confsearch-out.mae')
        energy_jobfile = self.with_ext(infile=infile, ext='_energy.in')
        energy_outfile = self.with_ext(infile=infile, ext='_energy-out.mae')
        energy_ifile = EnergyInput(use_substructure_file=False)
        energy_ifile.write(
            in_file=energy_jobfile,
            maefile=csearch_outfile,
            outfile=energy_outfile)

        csearch_jobfile = self.with_ext(infile=infile, ext='_confsearch.in')
        self.readfiles.append(energy_outfile)
        self.joblist_confsearch.append(csearch_jobfile)
        self.energy_listing = energy_jobfile

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

            water_molecules = analyze.evaluate_asl(st, "water")
            if (water_molecules):
                water = st.extract(water_molecules)
                protein = protein.merge(water)
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
            ifile = EmbraceMinimizationInput()
            ifile.write(maefile=mae_infile)
            mbaemini_jobfile = struc[0] + '.in'
            mbae_logfile = self.with_ext(infile=struc[0], ext='.log')
            self.readfiles.append(mbae_logfile)
            self.joblist_mbaemini.append(mbaemini_jobfile)

    def _writeSbcFile(self, infile):

        self.sbc_files = list()
        # radius = self.opts.shell_radius
        print("Radius: %s  Second Radius: all" % (self.radius))
        # print("Radius: %s  Second Radius: %s" % (radius, radius * 4))
        reader = structure.StructureReader(infile)
        st = reader.next()  # Protein
        largest_lig_st = reader.next()  # First ligand

        reader_ligands = structure.StructureReader(self.ligands)
        for lig_st in reader_ligands:
            if lig_st.atom_total > largest_lig_st.atom_total:
                largest_lig_st = lig_st

        print("Ligando mas grande: ", largest_lig_st)
        st = st.merge(largest_lig_st)

        binding_site_atoms = analyze.evaluate_asl(
            st, "fillres (all and within %s ligand) and not ligand" % self.radius)
        nearby_atoms = analyze.evaluate_asl(
            st, "not (ligand or fillres (all and within %s ligand))" % (self.radius))
        # nearby_atoms = analyze.evaluate_asl(
        #     st, "not (ligand or fillres (all and within %s ligand)) and fillres within %s ligand" % (radius, radius*4))
        name_file = infile.split('.')
        sbc_file = name_file[0] + '.sbc'
        self.sbc_files.append(sbc_file)
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

