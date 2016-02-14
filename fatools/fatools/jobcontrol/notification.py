import socket
import textwrap
import time
import traceback

from fatools.jobcontrol import JobStatus
from fatools.utils.enum import IntEnum
from fatools.utils.mail import send_mail

NotificationLevel = IntEnum('NotificationLevel', 'none queue failed all')

NOTIFICATION_PLACEHOLDERS = dict(
    job_changed=dict(
        subject='Job {job} {status}',
        template=textwrap.dedent("""\
            Hi there,

            Subjob '{job}' of queue '{queue}' changed status to \
{status_title} at {date} on machine {host}.
            {elapsed}
            Queue status
            ------------
            Completed = {done}
            Failed    = {failed}
            Active    = {active}
            Pending   = {pending}
            Total     = {total}

            Best regards,
            fatools.queue.

            Note: these notifications, that is, when a subjob changes status, \
can be omitted by setting the notitification level to anything but 'all'.
            """)),
    job_failed=dict(
        subject='Job {job} died',
        template=textwrap.dedent("""\
            Hi there,

            Sadly, subjob '{job}' of queue '{queue}' ended abnormally at \
{date} due to an unexpected internal error on machine {host}.
            No job control errors were found.

            Here are the last 50 lines of '{job}.log':

            {log_excerpt}

            Due to technical problems, job restart is not supported.
            However, the next job should have started already.

            Best regards,
            fatools.queue.
            """)),
    queue_aborted=dict(
        subject='Job queue {queue} ended abnormally',
        template=textwrap.dedent("""\
            Hi there,

            Something went wrong! Job queue '{queue}' aborted unexpectedly \
at {date} on machine {host}.

            So far, {done} of {total} job(s) succeeded; {failed} job(s) failed.
            Total run time was about {elapsed} on {cpu} processor(s).

            Here is the traceback of the exception that halted execution:

            {traceback}

            Due to technical problems, job restart is not supported.
            All active jobs ({active}) were killed.

            Best regards,
            fatools.queue.
            """)),
    queue_finished=dict(
        subject='Job queue {queue} ended normally',
        template=textwrap.dedent("""\
            Hi there,

            Job queue '{queue}' has finished successfully at {date} on \
machine {host}.

            Summary
            =======
            {done} of {total} job(s) succeeded; {failed} job(s) failed.
            Total run time about {elapsed} on {cpu} processor(s).
            {failed_section}
            Best regards,
            fatools.queue.
            """)))


def get_notification_info(queue, job=None):
    data = dict(queue=queue.name, host=socket.gethostname())
    if job is None:  # queue changed status
        data['date'] = time.ctime(queue._end_time)
        data['elapsed'] = queue.elapsed.format('long', limit=2)
        data['cpu'] = queue.total_cpu
        if queue._state is JobStatus.finished:
            if len(queue.failed_jobs) > 0:
                content = '\nFailed jobs:\n'
                for fj in queue.failed_jobs:
                    content += '* {}.\n'.format(fj.name)
                data['failed_section'] = content
            else:
                data['failed_section'] = ''
        elif queue._state is JobStatus.aborted:
            content = traceback.format_exc()[:-1].replace('\n', '\n    ')
            data['traceback'] = '    ' + content
    else:  # job changed status
        data['job'] = job.name
        data['date'] = time.ctime(job.end_time)
        data['status'] = str(job.state)
        data['status_title'] = str(job.state).title()
        if job.did_failed:
            content = job.log_excerpt(nlines=-50)[:-1].replace('\n', '\n    ')
            data['log_excerpt'] = '    ' + content
        elif job.state.terminated:
            template = 'Job took about {} on {} processor(s).\n'
            data['elapsed'] = template.format(
                job.elapsed.format('long', limit=2), queue.cpu_per_job)
        else:
            data['elapsed'] = ''

    job_states = ('done', 'active', 'pending', 'failed')
    for state, count in zip(job_states, queue.job_count()):
        data[state] = count
    data['total'] = queue.njobs
    return data


def get_notification_placeholder(queue, job=None):
    if queue._notification_level is NotificationLevel.none:
        return None
    elif queue._state.terminated and \
            queue._notification_level >= NotificationLevel.queue:
        key = 'queue_' + str(queue._state)
    elif job.state == JobStatus.died and \
            queue._notification_level >= NotificationLevel.failed:
        key = 'job_failed'
    elif queue._notification_level >= NotificationLevel.all:
        key = 'job_changed'
    else:
        return None
    return NOTIFICATION_PLACEHOLDERS[key]


def send_notification_if_needed(queue, job=None):
    placeholder = get_notification_placeholder(queue, job)
    if placeholder is None:
        return
    data = get_notification_info(queue, job)
    send_mail(
        recipient=queue._recipient,
        subject=placeholder['subject'].format(**data),
        content=placeholder['template'].format(**data))
