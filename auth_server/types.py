import uuid

from enum import Enum
from pydantic import BaseModel

class FolderType(str, Enum):
    """
    Type of special folder.
    """
    HOME = "home"
    INBOX = "inbox"


class OwnerType(str, Enum):
    """
    Type of owner for a special folder.

    Special folders can be owned by either individual users or groups.
    """
    USER = "user"
    GROUP = "group"


class Owner(BaseModel):
    owner_type: OwnerType
    owner_id: uuid.UUID

    @staticmethod
    def create_from(
        user_id: uuid.UUID | None = None,
        group_id: uuid.UUID | None = None
    ) -> "Owner":
        if group_id is not None:
            return Owner(owner_type=OwnerType.GROUP, owner_id=group_id)
        elif user_id is not None:
            return Owner(owner_type=OwnerType.USER, owner_id=user_id)
        else:
            raise ValueError("Either user_id or group_id must be provided")


class ResourceType(str, Enum):
    """Resources that can be owned"""
    NODE = "node"
    CUSTOM_FIELD = "custom_field"
    DOCUMENT_TYPE = "document_type"
    TAG = "tag"


class Resource(BaseModel):
    type: ResourceType
    id: uuid.UUID


class NodeResource(Resource):
    type: ResourceType = ResourceType.NODE
