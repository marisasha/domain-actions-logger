from pathlib import Path

from enum import Enum

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


class PermissionEnum(str, Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class GenderEnum(str, Enum):
    Male = "M"
    Female = "F"


def n_print(data):
    print("\n\n\n\n\n\n", data, "\n\n\n\n\n\n")
