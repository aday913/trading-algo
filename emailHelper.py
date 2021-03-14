from email.mime.text import MIMEText
from dotenv import load_dotenv
import smtplib, ssl
import email
import os

class Emailer(object):
    '''
    Emailer class that allows for the sending of 
    portfolio updates as they become available
    '''

    def __init__(self):
        self.port = 465
        self.server = 'smtp.gmail.com'

        load_dotenv()

        self.SENDER = os.getenv('SENDEREMAIL')
        self.RECEIVER = os.getenv('RECEIVEREMAIL')
        self.PASSWORD = os.getenv('EMAILPASSWORD')

    def sendMessage(self, message, subject='Weekly Update'):
        '''
        '''
        context = ssl.create_default_context()

        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = self.SENDER
        msg['To'] = self.RECEIVER

        with smtplib.SMTP_SSL(self.server, self.port, 
                            context=context) as server:
            server.login(self.SENDER, self.PASSWORD)
            server.sendmail(self.SENDER, self.RECEIVER, msg.as_string())
        print('Successfully sent the email!')

if __name__ == '__main__':
    emailBot = Emailer()
    emailBot.sendMessage(
        '''\
            Hey there! This is a test email from adaypython!
        '''
        )