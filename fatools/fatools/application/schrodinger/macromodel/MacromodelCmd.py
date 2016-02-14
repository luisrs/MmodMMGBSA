import os

from fatools.jobcontrol import (
    Cmd, CmdOption, CmdWithInputFiles, CpuOption, CpuHostOption)


class MacromodelCmd(Cmd):
    pass


class PrimeMMGBSACmd(Cmd):
    pass


class MacromodelWithInputCmd(MacromodelCmd, CmdWithInputFiles):
    ncpu = CpuOption('-NJOBS')
    jobname = CmdOption('-jobname', type=str, allow_none=True)
    host = CpuHostOption('-HOST')

    def _after_initialize(self):
        if self.jobname is None:
            self.jobname = os.path.splitext(self.filenames[0])[0]

    def _format_option_value(self, opt, val):
        if opt == 'jobname' and val == os.path.splitext(self.filenames[0])[0]:
                return None  # value is the default jobname
        return super(MacromodelWithInputCmd, self)._format_option_value(opt, val)


class PrimeMMGBSAWithInputCmd(PrimeMMGBSACmd, CmdWithInputFiles):
    jobname = CmdOption('-jobname', type=str, allow_none=True)
    host = CpuHostOption('-rflexdist 1')

    def _after_initialize(self):
        if self.jobname is None:
            self.jobname = os.path.splitext(self.filenames[0])[0]

    def _format_option_value(self, opt, val):
        if opt == 'jobname' and val == os.path.splitext(self.filenames[0])[0]:
                return None  # value is the default jobname
        return super(PrimeMMGBSAWithInputCmd, self)._format_option_value(opt, val)


class RunMacromodelCmd(MacromodelWithInputCmd):
    program = 'macromodel'


class RunPrimeMMGBSA(PrimeMMGBSAWithInputCmd):
    program = 'prime_mmgbsa'
