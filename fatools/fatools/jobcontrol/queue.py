import abc
import multiprocessing
import sys
import textwrap
import time

from fatools.core_ext.datetime import timedelta
from fatools.jobcontrol import Job, JobStatus
from fatools.jobcontrol.notification import (
    NotificationLevel, send_notification_if_needed)
from fatools.utils.func import select
from fatools.utils.mail import can_send_mail
from fatools.utils.tabular import Table

MAX_CPUS = multiprocessing.cpu_count()


class JobQueue(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, cpu=1, cpu_per_job=1, job_class=Job,
                 notify=None, recipient=None):
        self._name = name
        self.total_cpu, self.cpu_per_job = cpu, cpu_per_job
        self._job_class = job_class

        self._setup_notification_level(notify, recipient)

        self._state = None
        self._jobs = []
    jobs = property(lambda self: tuple(self._jobs))
    name = property(lambda self: self._name)
    njobs = property(lambda self: len(self._jobs))
    state = property(lambda self: self._state)

    @property
    def active_jobs(self):
        return self.jobs_with_status(JobStatus.started)

    @property
    def done_jobs(self):
        return self.jobs_with_status(JobStatus.finished)

    @property
    def elapsed(self):
        if self._state is None:
            return timedelta(seconds=0)
        if self._state is JobStatus.started:
            return timedelta(seconds=time.time() - self._start_time)
        return timedelta(seconds=self._end_time - self._start_time)

    @property
    def failed_jobs(self):
        return self.jobs_with_status(JobStatus.aborted, JobStatus.died)

    @property
    def max_simultaneous_jobs(self):
        return int(self.total_cpu / self.cpu_per_job)

    @property
    def pending_jobs(self):
        return self.jobs_with_status(None)

    @property
    def total_cpu(self):
        return self._total_cpu

    @total_cpu.setter
    def total_cpu(self, cpu):
        if cpu == 'all':
            cpu = MAX_CPUS
        self._total_cpu = cpu if cpu <= MAX_CPUS else MAX_CPUS

    @abc.abstractmethod
    def abort(self, job=None):
        return NotImplemented

    def add_job(self, cmd):
        if self.state is not None:
            raise Exception('launcher has started, cannot add more jobs')
        self._jobs.append(self._job_class(cmd))

    def job_count(self):
        return (len(self.done_jobs), len(self.active_jobs),
                len(self.pending_jobs), len(self.failed_jobs))

    def jobs_with_status(self, *states):
        return select(self._jobs, lambda job: job.state in states)

    def run_and_wait(self):
        self._setup()
        self._initialize_table()
        self._print_status_header()

        self._start_time = time.time()
        self._state = JobStatus.started

        try:
            self._launch_and_wait()
        except (Exception, KeyboardInterrupt) as err:
            self._handle_error(err)
        else:
            self._state = JobStatus.finished
        finally:
            self._end_time = time.time()
            self._print_status_footer()
            send_notification_if_needed(self)

    def _handle_error(self, err):
        self.abort()
        self._state = JobStatus.aborted
        if type(err) is KeyboardInterrupt:
            print('\nJob execution interrupted. All active jobs were killed.')
        else:
            print('\nSomething went wrong. Halting job execution.')
            raise

    def _initialize_table(self):
        ndigits = len(str(self.njobs))
        jobname_length = max(map(len, (j.name for j in self.jobs)))
        self.table = Table(
            colwidths=(ndigits,) * 4 + (8, jobname_length, 12, 4),
            headers=('C', 'A', 'P', 'F', 'Status', 'Jobname', 'Time', 'Info'),
            style='condensed',
            write_on_data=True, outfile=sys.stdout)
        self.table.cols[6].align = 'right'

    @abc.abstractmethod
    def _launch_and_wait(self):
        return NotImplemented

    def _print_status_footer(self):
        template = textwrap.dedent("""
            All jobs {} terminated.
            {done} of {total} job(s) succeeded; {failed} job(s) failed.
            Total run time about {elapsed}.

            Job queue ended {} at {date}.""")
        done, _, _, failed = self.job_count()
        print(template.format(
            'were' if self.state == JobStatus.aborted else 'has',
            'abnormally' if self.state == JobStatus.aborted else 'normally',
            done=done, total=self.njobs, failed=failed,
            elapsed=self.elapsed.format('long', limit=2), date=time.ctime()))

    def _print_status_header(self):
        template = textwrap.dedent("""\
            Job queue starting at {date}.

            Queue parameters
            ----------------
            Number of jobs           : {total}
            Number of available cpus : {cpu}
            Cpus per job             : {cpu_per_job}
            Max. simultaneous jobs   : {max_jobs}
            Notifications            : {notification}

            Starting jobs...
             C: Number of completed subjobs.
             A: Number of active subjobs (e.g., submitted, running).
             P: Number of pending/waiting subjobs.
             F: Number of failed (aka, died) subjobs.
            """)
        if self._notification_level is NotificationLevel.none:
            notification = 'disabled'
        else:
            notification = '{} ({})'.format(
                self._recipient, self._notification_level.name)
        print(template.format(
            date=time.ctime(), total=self.njobs, cpu=self.total_cpu,
            cpu_per_job=self.cpu_per_job, max_jobs=self.max_simultaneous_jobs,
            notification=notification))
        self.table.start_editing()

    @abc.abstractmethod
    def _setup(self):
        return NotImplemented

    def _setup_notification_level(self, level, recipient):
        if level is None or can_send_mail() is False or recipient is None:
            self._notification_level = NotificationLevel.none
        else:
            self._notification_level = NotificationLevel[level]
            if '@' not in recipient:
                msg = 'invalid recipient email address: {}'
                raise ValueError(msg.format(recipient))
            self._recipient = recipient

    def _update_job_status(self, job):
        job_time = job.elapsed.format('short') if job.is_terminated else \
            time.strftime('%b %d %H:%M', time.gmtime(job.start_time))
        self.table.addrow(
            self.job_count() + (str(job.state), job.name, job_time, job.id))
        send_notification_if_needed(self, job)
