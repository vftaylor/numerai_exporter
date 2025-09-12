from enum import StrEnum, IntEnum


class RoundState(StrEnum):
    RESOLVED = 'resolved'
    UNRESOLVED = 'unresolved'


class RoundingDP(IntEnum):
    ONE = 1
    FOUR = 4
