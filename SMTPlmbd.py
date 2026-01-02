import logging
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
#Final destination pattern
despattern = r"(---Final destination---)([\s\S]+)(---Final destination---)"
#Body content pattern
bdpattern = r"(---Final destination---)([\s\S]+)(---Final destination---)([\s\S]+)"

def lambda_handler(event, context):

    #despattern = r"(---Final destination---)([\s\S]+)(---Final destination---)"
    #bdpattern = r"(---Final destination---)([\s\S]+)(---Final destination---)([\s\S]+)"
    fnldest = ''        #Final destination 
    bdtxt = ''          #Body content
    attch = []          #Attachment

    response  = getWalkkmailSpn(event)

    rawmsg    = BytesParser(
                  policy=policy.default
                ).parsebytes(
                    response['Body'].read())

    emailsrc  = getSrc(rawmsg) 

    try:
        
        print("\n***Email source***\n", 
                emailsrc[2],
              "\n^^^Email source^^^\n"
        ) 

    except:
        print("\n***Failed on emailsrc[2]***\n")                     

    try:
        print("\n***Sending email***\n")

        sendEmail(
            "smtp.mail.us-east-1.awsapps.com",
            465,
            "walkk@walterkakool.ca",
            rawmsg
        )

        print("\n^^^Email sent^^^\n")

    except Exception as e:
        print("\n***sendEmail errors***\n",
                f"{e}",
                "\n^^^sendEmail errors^^^\n"
        ) 
         

def getWalkkmailSpn(event):
    
    record  = event['Records'][0]
    bktname = record['s3']['bucket']['name']
    objkey  = record['s3']['object']['key']

    return s3.get_object(
                          Bucket=bktname, 
                          Key=objkey
           ) 

def getSub(rawmsg):

    return rawmsg.get('Subject')


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

    returnstr = ""

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
                            #print(f"Found attachment: {filename}")
                            extractionattch = part.get_content()
                            
                            objkey = f"{os.path.basename(filename)}"
                            
                            s3.put_object(
                                Bucket="walkkmailattch",
                                Key=objkey,
                                Body=extractionattch
                            )
                            extracted_files.append(objkey)


        returnstr  = "{\n"
        returnstr += "'Function':'getAttch'\n"
        returnstr += "'Return': 0,\n"
        returnstr += "'Attachments':"
        returnstr += f"{extracted_files}"
        returnstr += "\n}\n"

        #return returnstr
        return extracted_files


    except Exception as e:

        returnstr  = "{\n"
        returnstr += "'Function':'getAttch'\n"
        returnstr += "'Return': 1,\n"
        returnstr += f"'Errors': {e}"
        returnstr += "\n}\n"  

        return returnstr     



def receiveEmail():
    
    return 0 


def sendEmail(  server, #"";  "smtp.mail.us-east-1.awsapps.com" 
                port,   #int; 465
                sdr,    #"";  "walkk@walterkakool.ca"
                rawmsg, #BytesParser
):
    inmsg       = rawmsg
    emailsrc  = getSrc(inmsg)

    outmsg = MIMEMultipart()

    if emailsrc[2] == "walter.kakool@unb.ca":

        bdtxt     = getBody(inmsg)        #This has final destination

        fnldest   = getDes(bdtxt,
                           despattern
                    ) 

        #No final destination inside
        bdtxt     = re.search(bdpattern, 
                              bdtxt
                    )

        outmsg['Subject'] = rawmsg.get('Subject')
        outmsg['From']    = sdr
        recepient         = fnldest[2][2:-2]
        outmsg['To']      = recepient        
        outmsg.attach(MIMEText(bdtxt[4], "plain"))
        extrfs = getAttch(rawmsg)

        for extrf in extrfs:
            s3_response = s3.get_object(
                            Bucket="walkkmailattch",
                            Key=extrf
                          ) 

            pdf_content = s3_response['Body'].read()
            attachment = MIMEApplication(pdf_content, Name=extrf)

            attachment.add_header(
                'Content-Disposition', 
                'attachment', 
                filename=extrf
            )

            outmsg.attach(attachment)

        print("Message ID:\n",
            ses.send_raw_email(
            Source=sdr,
            Destinations=[recepient],
            RawMessage={'Data': outmsg.as_string()}
            )
        )

"""
    #Test cases
    emailsrc  = getSrc(rawmsg)     
    bdtxt     = getBody(rawmsg)
    fnldest   = getDes(bdtxt, despattern) 

    bdtxt     = re.search(bdpattern, 
                          bdtxt
                ) 

    attchrepn = getAttch(rawmsg)
    #Printing out contents in test cases 

    try:
        print("\n***Current object in walkkmail:***\n",
          event['Records'][0]
               ['s3']['object']
               ['key'],
          "\n^^^Current object in walkkmail^^^\n"
        )

    except Exception as e:
        print(f"***Current object enounter errors:***\n",
              f"{e}\n",
              "^^^Current object enounter errors^^^\n"
        )  

    try:
        
        print("\n***Email source***\n", 
                emailsrc[2],
              "\n^^^Email source^^^\n"
        ) 

    except:
        print("\n***Failed on emailsrc[2]***\n") 

    try:      
        print("\n***Email plain content body***\n",
               bdtxt[4],
              "\n^^^Email plain content body^^^\n"
        ) 

    except:
        print("\n***Failed on bdtxt[4]***\n")         

    try:
        print("\n***Final destination***\n", 
                fnldest[2],
              "\n^^^Final destination^^^\n"
        ) 

    except:
        print("\n***Failed on fnldest[2]***\n")         

    try:
        print("\n***Printing attchrepn return***\n", 
                attchrepn,
              "\n^^^Printing attchrepn return^^^\n"
        ) 

    except:
        print("\n***Failed on attchrepn***\n")  
        
 
""" 
