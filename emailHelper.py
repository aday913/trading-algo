from dotenv import load_dotenv
import smtplib, ssl
import email
import os

SENDER = os.getenv('SENDER')
RECEIVER = os.getenv('RECEIVER')
PASSWORD = os.getenv('PASSWORD')

port = 465
smtp_server = 'smtp.gmail.com'

message = '''\
Subject: Test email!

Hey there! This is a test email from adaypython!
'''

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, 
                    context=context) as server:
    server.login(SENDER, PASSWORD)
    server.sendmail(SENDER, RECEIVER, message)

class Emailer(object):
    '''
    Emailer class that allows for the sending of 
    portfolio updates as they become available
    '''

    def __init__(self):
        self.port = 465
        self.server = 'smtp.gmail.com'

        load_dotenv()

        self.SENDER = os.getenv('SENDER')
        self.RECEIVER = os.getenv('RECEIVER')
        self.PASSWORD = os.getenv('PASSWORD')

    def sendMessage(self, message):
        '''
        '''
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.server, self.port, 
                            context=context) as server:
            server.login(self.SENDER, self.PASSWORD)
            server.sendmail(self.SENDER, self.RECEIVER, message)