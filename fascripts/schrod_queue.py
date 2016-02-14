"""Launch one or more calculations for Schrodinger products.
"""

from __future__ import print_function
import argparse
import multiprocessing
import os
import sys
import textwrap
from datetime import date
from fatools.application.schrodinger.macromodel.MacromodelCmd import (
    RunMacromodelCmd)
from fatools.application.schrodinger.jobcontrol import SchrodingerJobQueue

from fatools.application.schrodinger.macromodel.MMGBSA import (MmodMMGBSA)
from fatools.jobcontrol import NotificationLevel

from schrodinger.job import app
from schrodinger.utils import fileutils

import sys
sys.path.append('/home/luis/Desktop/FranciscoAdasme/fatools')

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)


class SchrodQueue(app.App):
    def backend(self):
        # MBAEMINI
        for radius in range(2, 5):
            print("RADIUS", radius)
            self.queue_mbaemini = SchrodingerJobQueue(
                self.getJobName(), self.opts.cpu, 1,
                notify=self.opts.notification_level,
                recipient=self.opts.recipient)
            print("INPUTFILES", self.input_files)
            mmgbsa = MmodMMGBSA(self.input_files)
            print(mmgbsa.jobs_mbaemini, 'JOBLIST_MBAEMINI')
            print(mmgbsa.jobs_confsearch, 'JOBLIST_CONFSEARCH')
            print(mmgbsa.readfiles, 'ReadFIles')
            print(mmgbsa.poseviewer_files, 'poseviewer_files')
            for job in mmgbsa.jobs_mbaemini:
                print(RunMacromodelCmd(job, ncpu=1))
                self.queue_mbaemini.add_job(RunMacromodelCmd(
                    job, ncpu=1, host='localhost'))
            self.queue_mbaemini.run_and_wait()

    # # CONFSEARCH
            confsearch = os.path.isfile('confsearch_ok')
            if(confsearch):
                print("CONFSEARCH realizado")
                result = mmgbsa.calculate_scoring_function(mmgbsa.readfiles)

            else:
                self.queue_confsearch = SchrodingerJobQueue(
                    self.getJobName(), self.opts.cpu, 4,
                    notify=self.opts.notification_level, recipient=self.opts.recipient)
                # mmgbsa = MmodMMGBSA(self.input_files)
                for job in mmgbsa.jobs_confsearch:
                    print(RunMacromodelCmd(job, ncpu=4, host='localhost:4'))
                    self.queue_confsearch.add_job(RunMacromodelCmd(
                        job, ncpu=4, host='localhost:4'))
                self.queue_confsearch.run_and_wait()
                file = open('confsearch_ok', 'w')   # Trying to create a new file or open one
                file.close()
                result = mmgbsa.calculate_scoring_function(mmgbsa.readfiles)

            if(result):
                print("Calculae scoring function complete.\n")
                for infile in mmgbsa.jobs_mbaemini:
                    os.remove(infile)

                for infile in mmgbsa.jobs_confsearch:
                    os.remove(infile)

                for infile in mmgbsa.sbc_files:
                    os.remove(infile)

                for infile in mmgbsa.readfiles:
                    if('energy' in infile):
                        pass
                    else:
                        os.remove(infile)



                # os.remove(self.getJobName() + '.restart')

                # mmgbsa.calculate_entropyRRHO()

    def commandLine(self, args):
        self.opts = SchrodQueue.parse_args(args)
        self.setJobName(self.opts.jobname)
        self.setProgramName(fileutils.get_basename(__file__))
        self.alwaysLocal()
        self.input_files = self.opts.files
        for f in self.input_files:
            self.addInputFile(f)
        return self.opts.files

    def print_queue_info(self):
        template = textwrap.dedent("""
            {file} was invoked with the following arguments:
             Jobname         : {jobname}
             Executable name : {executable}
             Number of cpu   : {cpu} out of {total_cpu}
             Cpu per job     : {cpu_per_job}
             Number of files : {total_file}""")
        print(template.format(
            jobname=self.getJobName(),
            # file=os.path.basename(__file__), executable='jaguar',
            file=os.path.basename(__file__), executable='macromodel',
            cpu=self.opts.cpu, total_cpu=multiprocessing.cpu_count(),
            cpu_per_job=self.opts.cpu_per_job,
            total_file=len(self.input_files)))

        for infile in self.input_files:
            print('  ' + os.path.basename(infile))
        print(' (Note that jobs will follow the above order)')

        if self.opts.recipient is not None:
            print(' Notify to       : {} ({})\n'.format(
                self.opts.recipient, self.opts.notification_level))

    @staticmethod
    def parse_args(args):
        parser = SchrodQueue.setup_parser()
        opts = parser.parse_args(args)
        if not fileutils.is_valid_jobname(opts.jobname):
            print('invalid jobname: {}'.format(opts.jobname))
            sys.exit(1)
        return opts

    @staticmethod
    def setup_parser():
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument(
            'files', nargs='+', metavar='FILE',
            help='One or more input files.')
        parser.add_argument(
            '-exec', dest='executable', required=True,
            choices=('jaguar', 'macromodel'),
            help='Executable name.')
        parser.add_argument(
            '-cpu', metavar='COUNT', type=int, default=1,
            help='Number of available cores to be used. '
                 'Defaults to the total number of cores on current machine '
                 '(%(default)s).')
        parser.add_argument(
            '-cpj', '--cpu-per-job', metavar='COUNT', type=int, default=1,
            help='Number of cores to use per job. This controls how many jobs '
                 'can be run simultaneously (i.e., <cpu> / <cpj>). '
                 'Default to %(default)s.')
        parser.add_argument(
            '-j', '--jobname',
            default='{}-{}'.format(
                fileutils.get_basename(__file__).replace('_', '-'),
                date.today().isoformat()),
            help='Job name. Defaults to \'%(default)s\'.')
        parser.add_argument(
            '--notify-to', metavar='EMAIL', default=None, dest='recipient',
            help='Send notification emails to this email address. '
                 'How often notification are sent can be set through '
                 '--notification-level option.')
        parser.add_argument(
            '--notification-level', default='failed', type=str.lower,
            choices=tuple(NotificationLevel.__members__),
            help='Control when notifications are sent. '
                 'Available options are: '
                 '\'none\' (do not send notifications), '
                 '\'queue\' (send a notification when queue ends or aborts), '
                 '\'failed\' (send a notification when a job fails, and the '
                 'above, default), and '
                 '\'all\' (send a notification when a job changes its status, '
                 'including all the above). '
                 'This option is ignored if no email address is entered.')
        parser.add_argument(
            '-r', '--radius', default=5, dest="shell_radius", type=int,
            help="Radius of the shell around the ligand. Default is 5 A.")
        return parser

if __name__ == '__main__':
    SchrodQueue(__file__, sys.argv[1:]).run()
