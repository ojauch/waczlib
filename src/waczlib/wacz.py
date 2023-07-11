from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict


class WaczArchive:
    def __init__(self, path: str) -> None:
        self._path = path

    def validate(self) -> None:
        """
        Check if the given wacz archive is valid according to the specification
        """
        pass

    def verify_checksums(self) -> Dict[str, bool]:
        """
        Check if the checksums of the files in the archive match with the checksums in the datapackage
        :return: dictionary with the paths of the files as keys and True if it is matching or False if not as values
        """
        pass

    def get_metadata(self) -> "WaczMetadata":
        """
        Get metadata from the wacz's datapackage
        :return: WaczMetadata object with the metadata of the archive
        """
        pass

    def __repr__(self):
        return f"WaczArchive(path='{self._path}')"


@dataclass
class WaczMetadata:
    wacz_version: str
    title: Optional[str]
    description: Optional[str]
    created: Optional[datetime]
    modified: Optional[datetime]
    software: Optional[str]
    mainPageUrl: Optional[str]
    mainPageDate: Optional[datetime]
