import sys

from datetime import datetime

if sys.version_info.minor < 11:
    import dateutil.parser


def parse_iso_8601_date(datestr) -> datetime:
    if sys.version_info.minor < 11:
        return dateutil.parser.isoparse(datestr)
    return datetime.fromisoformat(datestr)
