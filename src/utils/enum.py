from enum import Enum


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
