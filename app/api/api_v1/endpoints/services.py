from typing import List

from fastapi import APIRouter, Depends, UploadFile, File

from app.model.emails import EmailRequest
from app.utils.utils import execute_multipart_emailing_service, preprocess_request

router = APIRouter()


@router.post("/send-email", tags=[f'Email Request'])
async def sending_email_with_file_attachments(email_request: EmailRequest = Depends(EmailRequest.as_form),
                                                                    files: List[UploadFile] = File([])):
    """
    Send Multipart Email
    """
    # Pre-process the email request - clean the request received accordingly
    email_request_dict = preprocess_request(email_request)

    response = await execute_multipart_emailing_service(files, email_request_dict)

    return response['result']
