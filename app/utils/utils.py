import os
from typing import List
import aiofiles
from fastapi import UploadFile
from datetime import datetime
import shutil

from app.utils.mail import send_mail


async def execute_multipart_emailing_service(files: List[UploadFile], request):
    print("Email Request ==> ", request)
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

    if response['status']:

        remove_directory(file_data['path_to_folder'])  # Remove uploaded data
        return {'status': True, 'result': response}

    else:
        remove_directory(file_data['path_to_folder'])  # Remove uploaded data
        return {'status': False,'result': response}


def get_datetime():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


async def save_uploaded_files_to_wkdir(files):
    print({"filenames": [file.filename for file in files]})
    file_path = f"app/data/temp/upload_{get_datetime()}"
    os.mkdir(file_path)

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


def remove_directory(path):
    try:
        shutil.rmtree(path)
        print("Successfully cleaned uploaded files!")
    except:
        print("No files deleted.")
