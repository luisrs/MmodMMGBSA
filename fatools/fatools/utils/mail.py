import netrc
import smtplib
from email.mime.text import MIMEText

from fatools.utils.kernel import reraise
from fatools.utils.text import glued


# TODO add docstring
def can_send_mail(smtpserver='smtp.gmail.com'):
    try:
        secrets = netrc.netrc()
        if secrets.authenticators(smtpserver) is None:
            return False
    except IOError:
        return False
    except:
        raise
    else:
        return True


# TODO add docstring
def send_mail(recipient, subject, content, smtpserver='smtp.gmail.com',
              tls=True, usr=None, pwd=None):
    if usr is None or pwd is None:
        try:
            secrets = netrc.netrc()
            usr, _, pwd = secrets.authenticators(smtpserver)
        except Exception as err:
            msg = ('could not find email credentials for {server}.\n'
                   'make sure the .netrc file has a correct entry.')
            reraise(err, msg.format(server=smtpserver))
    if '@' not in usr:
        usr = '{}@{}'.format(usr, glued(smtpserver.split('.')[1:], '.'))

    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = usr
    msg['To'] = recipient

    s = smtplib.SMTP_SSL(smtpserver)
    if tls:
        # s.starttls()
        s.login(usr, pwd)
    s.sendmail(usr, [recipient], msg.as_string())
    s.quit()
