from enum import Enum


class Environment(str, Enum):
    PROD = "prod"
    PREPROD = "preprod"
    STAGE = "stage"


class UserDomain(str, Enum):
    CANARY = "canary"
    REGULAR = "regular"
