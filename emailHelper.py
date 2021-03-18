from email.mime.text import MIMEText
from dotenv import load_dotenv
import smtplib, ssl
import imapclient
import datetime
import logging
import email
import os

class Emailer(object):
    '''
    Emailer class that allows for the sending of 
    portfolio updates as they become available
    '''

    def __init__(self, debug=False):
        if debug:
            logging.basicConfig(level=logging.DEBUG,
                                format='%(name)s: %(message)s')
        else:
            logging.basicConfig(level=logging.INFO,
                                format='%(name)s: %(message)s')
        
        self.port = 465
        self.server = 'smtp.gmail.com'

        load_dotenv()

        self.SENDER = os.getenv('SENDEREMAIL')
        self.RECEIVER = os.getenv('RECEIVEREMAIL')
        self.PASSWORD = os.getenv('EMAILPASSWORD')

        self.seenIDs = []

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
        logging.debug('Successfully sent the email!')

    def readEmail(self):
        '''
        Brings in unread emails and parses out the body of the email if the
        email is from self.RECEIVER
        '''
        imapObj = imapclient.IMAPClient('imap.gmail.com', ssl=True)
        imapObj.login(self.SENDER, self.PASSWORD)
        imapObj.select_folder('INBOX', readonly=True)

        now = datetime.datetime.now()
        yesterday = (now + datetime.timedelta(days=-1)).strftime('%d-%b-%Y')
        UIDs = imapObj.search([u'SINCE', yesterday, u'UNSEEN'])
        messages = []
        for i in UIDs:
            if i not in self.seenIDs:
                rawMessage = imapObj.fetch(i, 'BODY[]')
                msg = email.message_from_bytes(rawMessage[i][b'BODY[]'])
                if msg['from'].split()[-1] == '<{}>'.format(self.RECEIVER):
                    if msg.is_multipart:
                        multi = msg.get_payload()
                        for j in multi:
                            temp = j.get_payload()
                            if temp[0] != '<':
                                messages.append(j.get_payload()[:-2])
                    else:
                        messages.append(msg.get_payload()[:-2])
                self.seenIDs.append(i)
        return messages

if __name__ == '__main__':
    emailBot = Emailer()
    emailBot.sendMessage(
        '''\
            Hey there! This is a test email!
        '''
        )
    print(emailBot.readEmail())