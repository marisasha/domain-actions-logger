from pathlib import Path

from enum import Enum

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


class PermissionEnum(str, Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    OWNER = "owner"

    def __str__(self):
        return self.value


class GenderEnum(str, Enum):
    Male = "M"
    Female = "F"

    def __str__(self):
        return self.value


class MoveEnum(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"

    def __str__(self):
        return self.value


def n_print(data):
    print("\n\n\n\n\n\n", data, "\n\n\n\n\n\n")
