import pytest

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
