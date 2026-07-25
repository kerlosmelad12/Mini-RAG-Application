from enum import Enum
class ResponseValues(Enum):
    NOT_APPROVED_TYPE="The file type is not approved"
    NOT_APPROVED_SIZE="The file size is not approved"
    
    FILE_APPROVED="The file is approved successfully"
    FILE_UPLOAD_FAILD="file upload failed"
    FILE_UPLOAD_SUCCSESS="file upload success"

    PROCESSING_SUCCESS = "processing_success"
    DELETED_CUNKS_SUCCESS="deleted_success"
    PROCESSING_FAILED = "processing_failed"

    NO_FILES_ERROR = "not_found_files"
    FILE_ID_ERROR = "no_file_found_with_this_id"

    NO_PROJECT_TO_EMBEDDING_DATA="no project found "
    NO_CHUNKS_FOR_EMBEDDING="no chunks to embedd"

    NO_DATA_ISTERSTEDIN_VECTOR="no data inserted in vector_db"
    INSERTED_SCUSSCFULLY_VECTORDB="data is inserted in vector db"
