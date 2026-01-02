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
#Bastion sender pattern
bspattern = r"([\s\S]+)(---Bastion---)([\s\S]+)(---Bastion---)"
#Body content pattern
bdpattern  = f"{bspattern}" + r"([\s\S]+)"

def lambda_handler(event, context):

    response  = getWalkkmailSpn(event)

    rawmsg    = BytesParser(
                  policy=policy.default
                ).parsebytes(
                    response['Body'].read()
                  )

    bdtxt     = getBody(rawmsg) 

    bastion   = getBastion(bdtxt,
                           bspattern
                ) 

    try:
        print("\n***Bastion***\n", 
                bastion[3],
              "\n^^^Bastion^^^\n"
        ) 

    except:
        print("\n***Failed on bastion[3]***\n") 

    try:
        print("\n***Sending email***\n")
        sendEmail(rawmsg)
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

def getBastion(bdtxt, bspattern):
    
    return re.search(bspattern, bdtxt) 
 
def getDes(bdtxt, despattern):
    return re.search(despattern, bdtxt)

def getAttch(rawmsg):
    extracted_files = []
    msg       = rawmsg
    bdtxt     = getBody(msg)

    bastion   = getBastion(bdtxt,
                           bspattern
                ) 

    attchBuck  = "" if bastion[3][2:-2] == "walkk@walterkakool.ca" else ""
    
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
                                Bucket=attchBuck,
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


def sendEmail(rawmsg):
    inmsg     = rawmsg
    emailsrc  = getSrc(inmsg)
    outmsg    = MIMEMultipart()

    if emailsrc[2] == "walterthaim@hotmail.com":
        #This has final destination && bastion
        bdtxt     = getBody(inmsg)        

        fnldest   = getDes(bdtxt,
                           despattern
                    ) 

        bastion   = getBastion(bdtxt,
                               bspattern
                    ) 

        #No final destination inside; [5]
        bdtxt     = re.search(bdpattern, 
                              bdtxt
                    )

        outmsg['Subject'] = rawmsg.get('Subject')
        bastionsdr        = bastion[3][2:-2]
        outmsg['From']    = bastionsdr
        recepient         = fnldest[2][2:-2]
        attchBuck         = "" if bastion[3][2:-2] == "walkk@walterkakool.ca" else ""
        outmsg['To']      = recepient        
        outmsg.attach(MIMEText(bdtxt[5], "plain"))
        #Only has text inside
        extrfs = getAttch(rawmsg)

        #Binding attachmentsss
        for extrf in extrfs:
            s3_response = s3.get_object(
                            Bucket=attchBuck,
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
            Source=bastionsdr,
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
