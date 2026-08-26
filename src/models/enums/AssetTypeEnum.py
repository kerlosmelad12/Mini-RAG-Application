from enum import Enum


class AssetTypeEnum(Enum):
    FILE = "file"
    SOUND = "sound"


class Assetlanguadge(Enum):
    EN = "en"
    AR = "ar"

    def to_deepl_code(self) -> str:
        mapping = {
            Assetlanguadge.AR: "AR",
            Assetlanguadge.EN: "EN-US",
        }
        return mapping[self]