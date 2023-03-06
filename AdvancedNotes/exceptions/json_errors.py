"""
Custom Json exceptions
"""


class JsonDumpingError(Exception):
    pass


class JsonReadingError(Exception):
    pass


class JsonLoadingError(Exception):
    pass


class EmptyJsonFileError(Exception):
    pass
