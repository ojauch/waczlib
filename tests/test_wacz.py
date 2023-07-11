from waczlib.wacz import WaczArchive


def test_wacz_archive_repr():
    archive = WaczArchive("test.wacz")
    assert repr(archive) == "WaczArchive(path='test.wacz')"
