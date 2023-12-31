import hashlib
import json
import re

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Generator, List
from contextlib import contextmanager
from zipfile import ZipFile

from waczlib.helpers import parse_iso_8601_date


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

            datapackage = self._get_datapackage()

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
        :raises InvalidWaczError: if the file isn't a valid wacz archive
        """
        checksums = {}

        datapackage = self._get_datapackage()

        for resource in datapackage['resources']:
            if 'hash' not in resource:
                continue

            hash_algo, hash_value = resource['hash'].split(':', 1)

            with self._get_zip() as zip_file:
                with zip_file.open(resource['path'], 'r') as file:
                    m = hashlib.new(hash_algo)
                    m.update(file.read())
                    calculated_digest = m.hexdigest()

                    checksums[resource['path']] = calculated_digest == hash_value

        return checksums

    def get_metadata(self) -> "WaczMetadata":
        """
        Get metadata from the wacz's datapackage
        :return: WaczMetadata object with the metadata of the archive
        :raises InvalidWaczError: if the file isn't a valid wacz archive
        """
        datapackage = self._get_datapackage()

        created = None
        if 'created' in datapackage:
            try:
                created = parse_iso_8601_date(datapackage['created'])
            except ValueError:
                raise InvalidWaczError('created must be an iso date time string')

        modified = None
        if 'modified' in datapackage:
            try:
                modified = parse_iso_8601_date(datapackage['modified'])
            except ValueError:
                raise InvalidWaczError('modified must be an iso date time string')

        main_page_date = None
        if 'main_page_date' in datapackage:
            try:
                main_page_date = parse_iso_8601_date(datapackage['main_page_date'])
            except ValueError:
                raise InvalidWaczError('main_page_date must be an iso date time string')

        return WaczMetadata(
            wacz_version=datapackage['wacz_version'],
            title=datapackage['title'] if 'title' in datapackage else None,
            description=datapackage['description'] if 'description' in datapackage else None,
            created=created,
            modified=modified,
            software=datapackage['software'] if 'software' in datapackage else None,
            main_page_url=datapackage['mainPageUrl'] if 'mainPageUrl' in datapackage else None,
            main_page_date=main_page_date
        )

    def get_pages(self) -> List["WaczPage"]:
        pages = []

        with self._get_zip() as zip_file:
            if 'pages/pages.jsonl' not in zip_file.namelist():
                raise InvalidWaczError("Does not contain pages/pages.jsonl")

            with zip_file.open('pages/pages.jsonl', 'r') as pages_file:
                for idx, line in enumerate(pages_file):
                    if idx == 0:
                        continue

                    self._validate_page(line)
                    page_data = json.loads(line)

                    page = WaczPage(
                        url=page_data['url'],
                        ts=parse_iso_8601_date(page_data['ts']),
                        title=page_data['title'] if 'title' in page_data else None,
                        id=page_data['id'] if 'id' in page_data else None,
                        text=page_data['text'] if 'text' in page_data else None,
                        size=page_data['size'] if 'size' in page_data else None
                    )
                    pages.append(page)

        return pages

    def __repr__(self) -> str:
        return f"WaczArchive(path='{self._path}')"

    @contextmanager
    def _get_zip(self) -> Generator[ZipFile, None, None]:
        try:
            zip_file = ZipFile(self._path, 'r')
            yield zip_file
        finally:
            zip_file.close()

    def _get_datapackage(self) -> dict:
        with self._get_zip() as zip_file:
            if 'datapackage.json' not in zip_file.namelist():
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

            if 'resources' not in datapackage or not isinstance(datapackage['resources'], list) \
                    or not datapackage['resources']:
                raise InvalidWaczError("resources must be set to an non empty array")

            return datapackage

    @staticmethod
    def _validate_pages(zip_file: ZipFile):
        with zip_file.open('pages/pages.jsonl', 'r') as pages_file:
            for idx, line in enumerate(pages_file.readlines()):
                if idx == 0:
                    continue
                WaczArchive._validate_page(line)

    @staticmethod
    def _validate_page(page_line: bytes):
        page = json.loads(page_line)

        if 'url' not in page:
            raise InvalidWaczError('page does not contain url property')

        if 'ts' not in page:
            raise InvalidWaczError('page does not contain ts property')


@dataclass
class WaczMetadata:
    wacz_version: str
    title: Optional[str]
    description: Optional[str]
    created: Optional[datetime]
    modified: Optional[datetime]
    software: Optional[str]
    main_page_url: Optional[str]
    main_page_date: Optional[datetime]


@dataclass
class WaczPage:
    url: str
    ts: datetime
    title: Optional[str]
    id: Optional[str]
    text: Optional[str]
    size: Optional[int]


class InvalidWaczError(Exception):
    def __init__(self, reason) -> None:
        self.reason = reason
