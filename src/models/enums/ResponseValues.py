from enum import Enum
class ResponseValues(Enum):
    NOT_APPROVED_TYPE="The file type is not approved"
    NOT_APPROVED_SIZE="The file size is not approved"
    
    FILE_APPROVED="The file is approved successfully"
    FILE_UPLOAD_FAILD="file upload failed"
    FILE_UPLOAD_SUCCSESS="file upload success"

    PROCESSING_SUCCESS = "processing_success"
    PROCESSING_FAILED = "processing_failed"