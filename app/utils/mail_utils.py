import boto3
import os

from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# The character encoding for the email.
CHARSET = "UTF-8"

# Create a new SES resource and specify a region.
ses_client = boto3.client('ses', region_name='ap-southeast-1')


def create_email_multipart_message(
        sender: str, sender_name: str, recipients: list, cc: list, bcc: list, title: str, text: str=None, body: str=None, attachments: list=None)\
        -> MIMEMultipart:
    print("Processing...")

    if text and body:
        # assign subtype - multipart/alternative
        content_subtype = 'alternative'
    else:
        # assign subtype - multipart/mixed
        content_subtype = 'mixed'

    # Instantiate a MIMEMultipart message object
    message = MIMEMultipart(content_subtype)
    message['Subject'] = title

    # if sender_name is provided, the format will be 'Sender Name <email@example.com>'
    if sender_name is None:
        message['From'] = f"{sender}"
    else:
        message['From'] = f"{sender_name} <{sender}>"

    message['To'] = ', '.join(recipients)
    message['CC'] = ', '.join(cc)
    message['BCC'] = ', '.join(bcc)

    # Record the MIME types of both parts:
    # text - defined as text/plain part
    if text:
        part = MIMEText(text, 'plain')
        message.attach(part)
    # body - defined as text/html part
    if body:
        part = MIMEText(body, 'html')
        message.attach(part)

    # Add attachments
    for attachment in attachments or []:
        with open(attachment, 'rb') as f:
            part = MIMEApplication(f.read())
            part.add_header('Content-Disposition',
                            'attachment',
                            filename=os.path.basename(attachment))
            message.attach(part)

    print("Multipart message creation done!")
    return message


def send_mail(
        sender: str, sender_name: str, recipients: list, cc: list, bcc: list, title: str, text: str=None, body: str=None, attachments: list=None) -> dict:

    try:
        print("Creating multipart message...")
        msg = create_email_multipart_message(sender, sender_name, recipients, cc, bcc, title, text, body,
                                             attachments)

        print("Sending Email to SES")
        # print(msg)

        # All emails in the requests including recipients, cc and bcc list need to be added in the destinations.
        destinations = []
        destinations.extend(recipients)
        destinations.extend(cc)
        destinations.extend(bcc)
        ses_response = ses_client.send_raw_email(Source=sender, Destinations=destinations, RawMessage={'Data': msg.as_string()})

    except ClientError as e:
        response = {"status": False, "message": e.response['Error']['Message'],
                    "message_id": "undefined",
                    "response": e.response}
        print("Response Key:", response.keys())
        print(response)
        return response
    else:
        response = {"status": True,
                "message": "Email Successfully Sent.",
                "message_id": ses_response['MessageId'],
                "response": ses_response}

        return response
