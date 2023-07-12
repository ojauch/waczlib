import pytest

from waczlib.helpers import parse_iso_8601_date
from waczlib.wacz import WaczArchive, InvalidWaczError


def test_wacz_archive_repr():
    archive = WaczArchive("test.wacz")
    assert repr(archive) == "WaczArchive(path='test.wacz')"


def test_validate_valid_wacz():
    archive = WaczArchive("test_assets/valid-example.wacz")
    archive.validate()


def test_validate_invalid_datapackage():
    archive = WaczArchive("test_assets/invalid-datapackage.wacz")
    with pytest.raises(InvalidWaczError) as e_info:
        archive.validate()
    assert e_info.value.reason == "resources must be set to an non empty array"


def test_validate_no_archives():
    archive = WaczArchive("test_assets/no-archives.wacz")
    with pytest.raises(InvalidWaczError) as e_info:
        archive.validate()
    assert e_info.value.reason == "Wacz must contain at least one web archive"


def test_validate_no_datapackage():
    archive = WaczArchive("test_assets/no-datapackage.wacz")
    with pytest.raises(InvalidWaczError) as e_info:
        archive.validate()
    assert e_info.value.reason == "Does not contain datapackage.json"


def test_validate_no_pages():
    archive = WaczArchive("test_assets/no-pages.wacz")
    with pytest.raises(InvalidWaczError) as e_info:
        archive.validate()
    assert e_info.value.reason == "Does not contain pages/pages.jsonl"


def test_validate_invalid_pages():
    archive = WaczArchive("test_assets/invalid-pages.wacz")
    with pytest.raises(InvalidWaczError) as e_info:
        archive.validate()
    assert e_info.value.reason == "page does not contain url property"


def test_get_metadata():
    archive = WaczArchive("test_assets/valid-example.wacz")
    metadata = archive.get_metadata()

    assert metadata.wacz_version == '1.1.1'
    assert metadata.title == 'valid-example'
    assert metadata.software == 'Webrecorder ArchiveWeb.page 0.10.1, using warcio.js 2.1.0'
    assert metadata.created == parse_iso_8601_date('2023-07-04T12:25:53.900Z')
    assert metadata.modified == parse_iso_8601_date('2023-07-04T12:26:05.132Z')


def test_get_metadata_invalid():
    archive = WaczArchive("test_assets/no-datapackage.wacz")
    with pytest.raises(InvalidWaczError):
        archive.get_metadata()


def test_verify_checksums():
    archive = WaczArchive("test_assets/valid-example.wacz")
    checksums = archive.verify_checksums()

    for result in checksums.values():
        assert result


def test_verify_checksums_invalid():
    archive = WaczArchive("test_assets/invalid-checksum.wacz")
    checksums = archive.verify_checksums()

    assert not checksums['archive/data.warc.gz']


def test_get_pages():
    archive = WaczArchive("test_assets/valid-example.wacz")
    pages = archive.get_pages()

    assert len(pages) == 1

    first_page = pages[0]
    assert first_page.title == 'Example Domain'
    assert first_page.url == 'https://example.org/'
    assert first_page.id == '49jh9ns3x0sqyifk124fng'
    assert first_page.size == 2512
    assert first_page.ts == parse_iso_8601_date("2023-07-04T12:25:55.274Z")
    assert first_page.text == "Example Domain\nExample Domain\nThis domain is for use in illustrative examples in " \
                              "documents. You may use this\n    domain in literature without prior coordination or " \
                              "asking for permission.\nMore information..."


def test_get_pages_invalid():
    archive = WaczArchive("test_assets/no-pages.wacz")
    with pytest.raises(InvalidWaczError):
        archive.get_pages()

    archive = WaczArchive("test_assets/invalid-pages.wacz")
    with pytest.raises(InvalidWaczError):
        archive.get_pages()
