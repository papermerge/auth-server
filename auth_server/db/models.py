import uuid
from datetime import datetime
from typing import List, Literal
from uuid import UUID

from sqlalchemy import ForeignKey, String, func, Column, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

HOME_TITLE = ".home"
INBOX_TITLE = ".inbox"


group_permissions_association = Table(
    "auth_group_permissions",
    Base.metadata,
    Column(
        "group_id",
        ForeignKey("auth_group.id"),
    ),
    Column(
        "permission_id",
        ForeignKey("auth_permission.id"),
    ),
)

user_groups_association = Table(
    "core_user_groups",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("core_user.id"),
    ),
    Column(
        "group_id",
        ForeignKey("auth_group.id"),
    ),
)

user_permissions_association = Table(
    "core_user_user_permissions",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("core_user.id"),
    ),
    Column(
        "permission_id",
        ForeignKey("auth_permission.id"),
    ),
)

class User(Base):
    __tablename__ = "core_user"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        insert_default=uuid.uuid4()
    )
    username: Mapped[str]
    email: Mapped[str]
    password: Mapped[str]
    first_name: Mapped[str] = mapped_column(default=' ')
    last_name: Mapped[str] = mapped_column(default=' ')
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_staff: Mapped[bool] = mapped_column(default=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    nodes: Mapped[List["Node"]] = relationship(
        back_populates="user",
        primaryjoin="User.id == Node.user_id"
    )
    home_folder_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "core_folder.basetreenode_ptr_id",
            deferrable=True,
            use_alter=True
        ),
        nullable=True
    )
    home_folder: Mapped['Folder'] = relationship(
        primaryjoin="User.home_folder_id == Folder.id",
        back_populates="user",
        viewonly=True
    )
    inbox_folder_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "core_folder.basetreenode_ptr_id",
            deferrable=True,
            use_alter=True
        ),
        nullable = True,
    )
    inbox_folder: Mapped['Folder'] = relationship(
        primaryjoin="User.home_folder_id == Folder.id",
        back_populates="user",
        viewonly=True
    )
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now()
    )
    date_joined: Mapped[datetime] = mapped_column(
        insert_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        onupdate=func.now()
    )
    permissions: Mapped[list["Permission"]] = relationship(
        secondary=user_permissions_association,
        back_populates="users"
    )
    groups: Mapped[list["Group"]] = relationship(
        secondary=user_groups_association,
        back_populates="users"
    )


CType = Literal["document", "folder"]


class Node(Base):
    __tablename__ = "core_basetreenode"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, insert_default=uuid.uuid4()
    )
    title: Mapped[str] = mapped_column(String(200))
    ctype: Mapped[CType]
    lang: Mapped[str] = mapped_column(String(8))
    tags: List[str] = []
    user: Mapped["User"] = relationship(
        back_populates="nodes",
        primaryjoin="User.id == Node.user_id"
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("core_user.id", use_alter=True)
    )
    parent_id: Mapped[UUID] = mapped_column(
        ForeignKey("core_basetreenode.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        onupdate=func.now()
    )

    __mapper_args__ = {
        "polymorphic_identity": "node",
        "polymorphic_on": "ctype",
    }

    def __repr__(self):
        return f"{self.__class__.__name__}({self.title!r})"


class Folder(Node):
    __tablename__ = "core_folder"

    id: Mapped[UUID] = mapped_column(
        'basetreenode_ptr_id',
        ForeignKey("core_basetreenode.id"),
        primary_key=True,
        insert_default=uuid.uuid4()
    )

    __mapper_args__ = {
        "polymorphic_identity": "folder",
    }


class Permission(Base):
    __tablename__ = "auth_permission"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    codename: Mapped[str]
    content_type_id: Mapped[int] = mapped_column(
        ForeignKey("django_content_type.id")
    )
    content_type: Mapped["ContentType"] = relationship()
    groups = relationship(
        "Group",
        secondary=group_permissions_association,
        back_populates="permissions"
    )
    users = relationship(
        "User",
        secondary=user_permissions_association,
        back_populates="permissions"
    )


class Group(Base):
    __tablename__ = "auth_group"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    permissions: Mapped[list["Permission"]] = relationship(
        secondary=group_permissions_association,
        back_populates="groups"
    )
    users: Mapped[list["User"]] = relationship(
        secondary=user_groups_association,
        back_populates="groups"
    )


class ContentType(Base):
    __tablename__ = "django_content_type"

    id: Mapped[int] = mapped_column(primary_key=True)
    app_label: Mapped[str]
    model: Mapped[str]
