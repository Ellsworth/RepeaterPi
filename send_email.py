import smtplib


def send(user, password, msg, recipient, subject):
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        msg = 'Subject: %s\n\n%s' % (subject, msg)
        server.ehlo()
        server.starttls()
        server.login(user, password)
        server.sendmail(user, recipient, msg)
        smtplib.SMTP()
    except:
        print("Error sending the email. Possible internet outage detected...")


