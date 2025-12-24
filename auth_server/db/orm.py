import uuid
from datetime import datetime
from enum import Enum
from typing import List, Literal
from uuid import UUID

from sqlalchemy import ForeignKey, String, func, Column, Table, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, TIMESTAMP
from sqlalchemy import Enum as SQLEnum
from .base import Base

HOME_TITLE = "home"
INBOX_TITLE = "inbox"


class OwnerType(str, Enum):
    """Type of owner for a special folder."""

    USER = "user"
    GROUP = "group"


class FolderType(str, Enum):
    """Type of special folder."""

    HOME = "home"
    INBOX = "inbox"


roles_permissions_association = Table(
    "roles_permissions",
    Base.metadata,
    Column(
        "role_id",
        ForeignKey("roles.id"),
    ),
    Column(
        "permission_id",
        ForeignKey("permissions.id"),
    ),
)

user_groups_association = Table(
    "users_groups",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("users.id"),
    ),
    Column(
        "group_id",
        ForeignKey("groups.id"),
    ),
)

users_roles_association = Table(
    "users_roles",
    Base.metadata,
    Column(
        "role_id",
        ForeignKey("roles.id"),
    ),
    Column(
        "user_id",
        ForeignKey("users.id"),
    ),
)


class SpecialFolder(Base):
    """
    Junction table linking users/groups to their special folders.

    This table serves as a junction between users/groups and their special folders
    (home, inbox, and future folder types).
    """

    __tablename__ = "special_folders"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    owner_type: Mapped[OwnerType] = mapped_column(
        SQLEnum(
            OwnerType,
            name="owner_type_enum",
            values_callable=lambda x: [e.value for e in x],
            create_type=True,
        ),
        nullable=False,
        index=True,
    )

    owner_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    folder_type: Mapped[FolderType] = mapped_column(
        SQLEnum(
            FolderType,
            name="folder_type_enum",
            values_callable=lambda x: [e.value for e in x],
            create_type=True,
        ),
        nullable=False,
    )

    folder_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("folders.node_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    folder: Mapped["Folder"] = relationship(
        "Folder", foreign_keys=[folder_id], lazy="joined", viewonly=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "owner_type", "owner_id", "folder_type", name="uq_special_folder_per_owner"
        ),
        Index("idx_special_folders_owner", "owner_type", "owner_id"),
        Index("idx_special_folders_folder_id", "folder_id"),
    )

    def __repr__(self):
        return (
            f"SpecialFolder("
            f"owner={self.owner_type.value}:{self.owner_id}, "
            f"type={self.folder_type.value}, "
            f"folder_id={self.folder_id})"
        )


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, insert_default=uuid.uuid4())
    username: Mapped[str]
    email: Mapped[str]
    password: Mapped[str]
    first_name: Mapped[str] = mapped_column(default=" ")
    last_name: Mapped[str] = mapped_column(default=" ")
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_staff: Mapped[bool] = mapped_column(default=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    special_folders: Mapped[list["SpecialFolder"]] = relationship(
        "SpecialFolder",
        primaryjoin=(
            "and_("
            "foreign(SpecialFolder.owner_id) == User.id, "
            "SpecialFolder.owner_type == 'user'"
            ")"
        ),
        viewonly=True,
        lazy="selectin",
        cascade="delete",
    )

    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
    date_joined: Mapped[datetime] = mapped_column(insert_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(), onupdate=func.now()
    )
    roles: Mapped[list["Role"]] = relationship(  # noqa: F821
        secondary=users_roles_association, back_populates="users"
    )
    groups: Mapped[list["Group"]] = relationship(
        secondary=user_groups_association, back_populates="users"
    )

    @property
    def home_folder_id(self) -> UUID | None:
        """
        Get the home folder ID for this user.

        This property provides backward compatibility with code that expects
        home_folder_id to be a column on the User model.
        """
        for sf in self.special_folders:
            if sf.folder_type == FolderType.HOME:
                return sf.folder_id
        return None

    @property
    def inbox_folder_id(self) -> UUID | None:
        """
        Get the inbox folder ID for this user.

        This property provides backward compatibility with code that expects
        inbox_folder_id to be a column on the User model.
        """
        for sf in self.special_folders:
            if sf.folder_type == FolderType.INBOX:
                return sf.folder_id
        return None

    @property
    def home_folder(self) -> "Folder | None":
        """Get the home Folder object for this user."""
        for sf in self.special_folders:
            if sf.folder_type == FolderType.HOME:
                return sf.folder
        return None

    @property
    def inbox_folder(self) -> "Folder | None":
        """Get the inbox Folder object for this user."""
        for sf in self.special_folders:
            if sf.folder_type == FolderType.INBOX:
                return sf.folder
        return None

    __mapper_args__ = {"confirm_deleted_rows": False}


CType = Literal["document", "folder"]


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[UUID] = mapped_column(primary_key=True, insert_default=uuid.uuid4())
    title: Mapped[str] = mapped_column(String(200))
    ctype: Mapped[CType]
    lang: Mapped[str] = mapped_column(String(8))
    tags: List[str] = []
    parent_id: Mapped[UUID] = mapped_column(ForeignKey("nodes.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(), onupdate=func.now()
    )

    __mapper_args__ = {
        "polymorphic_identity": "node",
        "polymorphic_on": "ctype",
    }

    def __repr__(self):
        return f"{self.__class__.__name__}({self.title!r})"


class Folder(Node):
    __tablename__ = "folders"

    id: Mapped[UUID] = mapped_column(
        "node_id",
        ForeignKey("nodes.id", ondelete="CASCADE"),
        primary_key=True,
        insert_default=uuid.uuid4,
    )

    __mapper_args__ = {
        "polymorphic_identity": "folder",
    }


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    codename: Mapped[str]
    roles = relationship(
        "Role", secondary=roles_permissions_association, back_populates="permissions"
    )


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    users: Mapped[list["User"]] = relationship(
        secondary=user_groups_association, back_populates="groups"
    )


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(unique=True)
    permissions: Mapped[list["Permission"]] = relationship(
        secondary=roles_permissions_association, back_populates="roles"
    )
    users: Mapped[list["User"]] = relationship(  # noqa: F821
        secondary=users_roles_association, back_populates="roles"
    )
