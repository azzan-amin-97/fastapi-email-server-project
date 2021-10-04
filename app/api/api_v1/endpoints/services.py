from typing import List

from fastapi import APIRouter, Depends, UploadFile, File

from app.model.models import EmailRequest
from app.utils.utils import execute_multipart_emailing_service

router = APIRouter()


@router.post("/send-email", tags=[f'Email Request'])
async def execute_filtering_and_sending_email_with_file_attachments(email_request: EmailRequest = Depends(EmailRequest.as_form),
                                                                    files: List[UploadFile] = File([])):
    """
    Your Endpoint Description here
    """
    email_request_dict = dict(email_request)
    print(email_request_dict)
    response = execute_multipart_emailing_service(files, email_request_dict)

    return {"result": "test"}
