import json
from datetime import datetime, timedelta, timezone


DATE_FORMAT_JIRA = "%Y-%m-%dT%H:%M:%S.%f%z"
DATE_FORMAT_OWN = "%Y-%m-%d %H:%M:%S %f %z"


def parse_date_jira(date_str):
    return datetime.strptime(date_str, DATE_FORMAT_JIRA)


def parse_date_own(date_str):
    return datetime.strptime(date_str, DATE_FORMAT_OWN)


class CustomDatesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime(DATE_FORMAT_OWN)
        return str(obj)


class JiraDatesDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    @staticmethod
    def object_hook(source):
        for k, v in source.items():
            if isinstance(v, str):
                try:
                    source[k] = datetime.strptime(str(v), DATE_FORMAT_JIRA)
                except:
                    pass
        return source


# You haven't seen that
class OwnDatesDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, source):
        for k, v in source.items():
            if isinstance(v, str):
                try:
                    source[k] = datetime.strptime(str(v), DATE_FORMAT_OWN)
                except:
                    pass
        return source


def tz():
    return timezone(timedelta(hours=3))
