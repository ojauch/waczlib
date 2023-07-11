import pytest

from datetime import datetime

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
    assert metadata.created == datetime.fromisoformat('2023-07-04T12:25:53.900Z')
    assert metadata.modified == datetime.fromisoformat('2023-07-04T12:26:05.132Z')


def test_get_metadata_invalid():
    archive = WaczArchive("test_assets/no-datapackage.wacz")
    with pytest.raises(InvalidWaczError):
        archive.get_metadata()
