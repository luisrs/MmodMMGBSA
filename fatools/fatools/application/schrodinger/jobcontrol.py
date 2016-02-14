import glob
import logging
import os
import StringIO

from schrodinger.job.queue import JobControlJob, JobDJ, NOLIMIT
from fatools.jobcontrol import Job, JobQueue, JobStatus
from fatools.utils.func import update_dict
from fatools.utils.kernel import redirect_stream

logging.disable(logging.ERROR)  # avoids message printed by JodDJ
_null_stream = StringIO.StringIO()  # used to redirect JobDJ undesired output


class SchrodingerJob(Job):
    def _clean_failed_output(self):
        """Delete <jobname>*.failed.* output files."""
        for filepath in glob.iglob('{}.*.failed.*'.format(self.name)):
            os.remove(filepath)

    def _update(self):
        """Force update from internal JobDJ job object."""
        self.id = self._dj_job._job_id
        if self._dj_job.state == 'active':
            self._state = JobStatus.started
        elif self._dj_job.state == 'done':
            self._state = JobStatus.finished
        elif self._dj_job.state == 'failed':
            self._state = JobStatus.died
            self._clean_failed_output()  # avoids *.failed.* files
        else:
            self._state = None


class SchrodingerJobQueue(JobQueue):
    def __init__(self, *args, **kwargs):
        update_dict(kwargs, dict(job_class=SchrodingerJob))
        super(SchrodingerJobQueue, self).__init__(*args, **kwargs)

    def abort(self, job=None):
        if job is None:
            self.job_dj.killJobs()
        else:
            job._dj_job.kill()

    def _launch_and_wait(self):
        with redirect_stream(stdout=_null_stream):
            for dj_job in self.job_dj.updatedJobs():
                dj_job._wrapper._update()
                with redirect_stream(stdout='orig'):
                    self._update_job_status(dj_job._wrapper)

    def _setup(self):
        self.job_dj = JobDJ(
            hosts=[('localhost', self.max_simultaneous_jobs)],
            max_failures=NOLIMIT)  # avoids stop on job failure
        for job in self.jobs:
            dj_job = JobControlJob(list(job.cmd.args))
            dj_job._wrapper = job
            job._dj_job = dj_job
            self.job_dj.addJob(dj_job)
