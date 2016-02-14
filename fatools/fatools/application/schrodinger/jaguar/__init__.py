import os

from fatools.jobcontrol import Cmd, CmdOption, CmdWithInputFiles, CpuOption


class JaguarCmd(Cmd):
    pass


class JaguarWithInputCmd(JaguarCmd, CmdWithInputFiles):
    ncpu = CpuOption('-TPP')
    jobname = CmdOption('-jobname', type=str, allow_none=True)

    def _after_initialize(self):
        if self.jobname is None:
            self.jobname = os.path.splitext(self.filenames[0])[0]

    def _format_option_value(self, opt, val):
        if opt == 'jobname' and val == os.path.splitext(self.filenames[0])[0]:
                return None  # value is the default jobname
        return super(JaguarWithInputCmd, self)._format_option_value(opt, val)


class RunJaguarCmd(JaguarWithInputCmd):
    program = 'jaguar run'
