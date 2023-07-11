import json
import re

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Generator
from contextlib import contextmanager
from zipfile import ZipFile


class WaczArchive:
    def __init__(self, path: str) -> None:
        self._path = path

    def validate(self) -> None:
        """
        Check if the given wacz archive is valid according to the specification

        :raises InvalidWaczError: if the archive is invalid
        """
        with self._get_zip() as zip_file:
            files = zip_file.namelist()

            if 'datapackage.json' not in files:
                raise InvalidWaczError("Does not contain datapackage.json")

            with zip_file.open('datapackage.json') as datapackage_file:
                try:
                    datapackage = json.load(datapackage_file)
                except json.JSONDecodeError:
                    raise InvalidWaczError("datapackage.json is not a valid JSON file")

            if 'profile' not in datapackage or datapackage['profile'] != 'data-package':
                raise InvalidWaczError("profile must be set to 'data-package'")

            if 'wacz_version' not in datapackage:
                raise InvalidWaczError("wacz_version must be set")

            if 'resources' not in datapackage or type(datapackage['resources']) != list \
                    or len(datapackage['resources']) == 0:
                raise InvalidWaczError("resources must be set to an non empty array")

            archive_regex = re.compile(r'archive/.+\.warc(\.gz)?')
            archive_files = [file for file in files if archive_regex.fullmatch(file)]
            if len(archive_files) == 0:
                raise InvalidWaczError("Wacz must contain at least one web archive")

            index_regex = re.compile(r'indexes/.+\.cdx(\.gz)?')
            index_files = [file for file in files if index_regex.fullmatch(file)]
            if len(index_files) == 0:
                raise InvalidWaczError("Wacz must contain at least one index file")

            if 'pages/pages.jsonl' not in files:
                raise InvalidWaczError('Does not contain pages/pages.jsonl')

            self._validate_pages(zip_file)

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

    def __repr__(self) -> str:
        return f"WaczArchive(path='{self._path}')"

    @contextmanager
    def _get_zip(self) -> Generator[ZipFile, None, None]:
        try:
            zip_file = ZipFile(self._path, 'r')
            yield zip_file
        finally:
            zip_file.close()

    @staticmethod
    def _validate_pages(zip_file: ZipFile):
        with zip_file.open('pages/pages.jsonl', 'r') as pages_file:
            for idx, line in enumerate(pages_file.readlines()):
                if idx == 0:
                    continue

                pages = json.loads(line)

                if 'url' not in pages:
                    raise InvalidWaczError('page does not contain url property')

                if 'ts' not in pages:
                    raise InvalidWaczError('page does not contain ts property')


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


class InvalidWaczError(Exception):
    def __init__(self, reason) -> None:
        self.reason = reason
