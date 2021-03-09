import smtplib, ssl
import email

from dotenv import load_dotenv

import os
load_dotenv()

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