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


def prepare_multipart_message(
        sender: str, sender_name: str, recipients: list, cc: list, bcc: list, title: str, text: str=None, body: str=None, attachments: list=None)\
        -> MIMEMultipart:
    print("Processing...")

    multipart_content_subtype = 'alternative' if text and body else 'mixed'
    msg = MIMEMultipart(multipart_content_subtype)
    msg['Subject'] = title

    if sender_name is None:
        msg['From'] = f"{sender}"
    else:
        msg['From'] = f"{sender_name} <{sender}>"

    msg['To'] = ', '.join(recipients)
    msg['CC'] = ', '.join(cc)
    msg['BCC'] = ', '.join(bcc)

    # Record the MIME types of both parts - text/plain and text/html.
    # According to RFC 2046, the last part of a multipart message, in this case the HTML message, is best and preferred.
    if text:
        part = MIMEText(text, 'plain')
        msg.attach(part)
    if body:
        part = MIMEText(body, 'html')
        msg.attach(part)

    # Add attachments
    for attachment in attachments or []:
        with open(attachment, 'rb') as f:
            part = MIMEApplication(f.read())
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment))
            msg.attach(part)
    print("Multipart message creation done!")
    return msg


def send_mail(
        sender: str, sender_name: str, recipients: list, cc: list, bcc: list, title: str, text: str=None, body: str=None, attachments: list=None) -> dict:

    """
    Send email to recipients. Sends one mail to all recipients.
    The sender needs to be a verified email in SES.
    """

    try:
        print("Im in send_mail!")
        print("Creating multipart message...")
        msg = prepare_multipart_message(sender, sender_name, recipients, cc, bcc, title, text, body,
                                        attachments)

        print("Sending Email to SES")
        # print(msg)

        destinations = []
        destinations.extend(recipients)
        destinations.extend(cc)
        destinations.extend(bcc)

        response = ses_client.send_raw_email(
            Source=sender,
            Destinations=destinations,
            RawMessage={'Data': msg.as_string()})

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
                "message_id": response['MessageId'],
                "response": response}

        return response
