from enum import Enum


class SoundProviderEnums(Enum):
    WHISPER = "WHISPER"


class WhisperDeviceEnums(Enum):
    CPU = "cpu"
    CUDA = "cuda"


class WhisperComputeTypeEnums(Enum):
    INT8 = "int8"
    FLOAT16 = "float16"
    FLOAT32 = "float32"


class WhisperModelSizeEnums(Enum):
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE_V3 = "large-v3"



 