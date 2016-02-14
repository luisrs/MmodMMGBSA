import time

from fatools.core_ext.datetime import timedelta
from fatools.jobcontrol import Cmd
from fatools.utils.enum import Enum
from fatools.utils.text import excerpt


class JobStatus(Enum):
    started = 'started'
    finished = 'finished'
    aborted = 'aborted'
    died = 'died'

    def __str__(self):
        return str(self.value)

    @property
    def terminated(self):
        return self in (JobStatus.finished, JobStatus.aborted, JobStatus.died)


class Job(object):
    def __init__(self, cmd):
        self._cmd = Cmd(cmd) if not isinstance(cmd, Cmd) else cmd
        self._state = None
        self._start_time, self._end_time = None, None
    cmd = property(lambda self: self._cmd)
    end_time = property(lambda self: self._end_time)
    is_terminated = property(lambda self: self.state.terminated)
    name = property(lambda self: self.cmd.jobname)
    start_time = property(lambda self: self._start_time)
    state = property(lambda self: self._state)

    did_failed = property(lambda self: self._state is JobStatus.died)

    def __setattr__(self, name, value):
        if name == '_state':
            if value == JobStatus.started:
                self._start_time = time.time()
            else:
                self._end_time = time.time()
        super(Job, self).__setattr__(name, value)

    @property
    def elapsed(self):
        if self.start_time is None:
            return timedelta(seconds=0)
        if self.end_time is None:
            return timedelta(seconds=time.time() - self.start_time)
        return timedelta(seconds=self.end_time - self.start_time)

    def log_excerpt(self, nlines=None):
        with open(self.name + '.log') as f:
            content = f.read()
        return excerpt(content, nlines=nlines)
