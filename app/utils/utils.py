import os
from typing import List
import aiofiles
from fastapi import UploadFile
from datetime import datetime
import shutil

from app.model.emails import EmailRequest
from app.utils.mail_utils import send_mail


def get_datetime():
    # return a current datetime string
    return datetime.now().strftime("%Y%m%d_%H%M%S")


async def execute_multipart_emailing_service(files: List[UploadFile], request):
    print("Email Request ==> ", request)

    # Save uploaded files to work directory -->  app/data/tmp
    file_data = await save_uploaded_files_to_wkdir(files)
    # try:
    print("\n===================================")
    print("Send Email Request to SES")
    print("===================================")
    response = send_mail(sender=request['sender'],
                         sender_name=request['sender_name'],
                         recipients=request['recipient'],
                         cc=request['cc'], bcc=request['bcc'],
                         title=request['subject'],
                         text=request['text'],
                         body=request['body'],
                         attachments=file_data['list_files'])

    # Email Sending Request is done, remove the uploaded files in the local directory
    if response['status']:
        remove_directory(file_data['path_to_folder'])  # Remove uploaded data
        return {'status': True, 'result': response}

    else:
        remove_directory(file_data['path_to_folder'])  # Remove uploaded data
        return {'status': False,'result': response}


async def save_uploaded_files_to_wkdir(files):
    # Create temporary folder for storing uploaded files
    file_path = f"app/data/temp/upload_{get_datetime()}"
    os.mkdir(file_path)

    # save the file in local directory and get the list of files
    list_files = []
    for file in files:
        _file_name = os.path.join(file_path, file.filename)
        print("File Name: ", _file_name)
        async with aiofiles.open(_file_name, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write
        list_files.append(_file_name)

    return {
        "path_to_folder": file_path,
        "list_files": list_files,
    }


def preprocess_request(email_request: EmailRequest):
    # Convert EmailRequest object to Python Dictionary format
    request = dict(email_request)
    # Check if recipient is None Type or an Empty String
    if not request['recipient'] or ((len(request['recipient']) == 1) and (request['recipient'][0] == '')):
        request.update({'recipient': []})
    else:
        request.update({'recipient': request['recipient'][0].split(',')})

    # Check if cc is None Type or an Empty String
    if not request['cc'] or ((len(request['cc']) == 1) and (request['cc'][0] == '')):
        request.update({'cc': []})
    else:
        request.update({'cc': request['cc'][0].split(',')})

    # Check if bcc is None Type or an Empty String
    if not request['bcc'] or ((len(request['bcc']) == 1) and (request['bcc'][0] == '')):
        request.update({'bcc': []})
    else:
        request.update({'bcc': request['bcc'][0].split(',')})

    return request


def remove_directory(path):
    try:
        # remove file based on the given param arg value
        shutil.rmtree(path)
        print("Successfully cleaned uploaded files!")
    except:
        print("No files deleted.")
