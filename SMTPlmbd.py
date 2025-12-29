import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
import re 
import boto3
import email
import datetime
from email import policy
from email.parser import BytesParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

s3 = boto3.client('s3')
ses = boto3.client('ses')

def lambda_handler(event, context):
    despattern = r"(---Final destination---)([\s\S]+)(---Final destination---)"
    bdpattern = r"(---Final destination---)([\s\S]+)(---Final destination---)([\s\S]+)"
    fnldest = ''        #Final destination 
    bdtxt = ''          #Body content
    attch = []          #Attachment

    response  = getWalkkmailSpn(event)

    rawmsg    = BytesParser(
                  policy=policy.default
                ).parsebytes(
                    response['Body'].read())

    emailsrc  = getSrc(rawmsg)     
    bdtxt     = getBody(rawmsg)
    fnldest   = getDes(bdtxt, despattern) 

    try:
        print("\n***Email source***\n", 
                emailsrc[2],
              "\n***Email source***\n"
        ) 

    except:
        print("\nFailed on emailsrc[2]\n") 

    try:
        print("\n***Final destination***\n", 
                fnldest[2],
              "\n***Final destination***\n"
        ) 

    except:
        print("\nFailed on fnldest[2]\n")           

    send_email_via_workmail()

def sendEmail(
                server, #""
                port,   #int
                msg):

    srv          = server
    prt          = port
    sdr          = sender
    sdpssw       = send_password
    repnt        = recipient
    txt          = text

    msg          = MIMEMultipart()

    smtp_server = "smtp.mail.us-east-1.awsapps.com" 
    smtp_port = 465
    sender_email = "walkk@walterkakool.ca"
    sender_password = "" 
    recipient_email = "walter.kakool@unb.ca"

    msg["From"] = sdr
    msg["To"]   = sdr
    msg["Subject"] = txt[0]
    msg.attach(MIMEText(txt[1], "plain"))    #Only body text

    try:
        ses.send_raw_email(
            Source=sender_email,
            Destinations=[recipient_email],
            RawMessage={'Data': message.as_string()}
        )

    except Exception as e:
        print(f"Error: {e}")   


def getWalkkmailSpn(event):
    
    record  = event['Records'][0]
    bktname = record['s3']['bucket']['name']
    objkey  = record['s3']['object']['key']

    return s3.get_object(
                          Bucket=bktname, 
                          Key=objkey
           ) 

def getBody(rawmsg):
    if rawmsg.is_multipart():
        for part in rawmsg.walk():
            ctype = part.get_content_type()
            cdisp = part.get('Content-Disposition')
            
            if ctype == 'text/plain' and cdisp is None:
                return part.get_content()
            
    elif rawmsg.get_content_type() == 'text/plain':
        return msg.get_content()
        
    return ""

def getSrc(rawmsg):

    result = re.search(r"(.*?)\s+<(.*?)>", 
               rawmsg.get('From')
             )
    return result
 
def getDes(bdtxt, despattern):
    return re.search(despattern, bdtxt)

def getAttch(rawmsg):
    extracted_files = []
    msg = rawmsg

    try:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue

                content_disposition = part.get("Content-Disposition", 
                                               None
                                      )
                
                if content_disposition:
                    disposition_type = content_disposition.strip().split(";")[0].lower()
                    
                    if disposition_type in ('attachment', 'inline'):
                        filename = part.get_filename()
                        
                        if filename:
                            print(f"Found attachment: {filename}")
                            file_payload = part.get_content()
                            
                            destination_key = f"extracted/{os.path.basename(filename)}"
                            
                            s3.put_object(
                                Bucket=source_bucket,
                                Key=destination_key,
                                Body=file_payload
                            )
                            extracted_files.append(destination_key)
        else:
            print("Email has no attachments.")

        return {
            'statusCode': 200,
            'body': json.dumps(f"Success. Attachment extracted: {extracted_files}")
        }

    except Exception as e:
        print(f"Errors processing email: {str(e)}")
        raise e

        return 1

    return 0           

def receiveEmail():
    
    return 0
