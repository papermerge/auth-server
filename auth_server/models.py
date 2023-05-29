import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .database import Base


HOME_TITLE = ".home"
INBOX_TITLE = ".inbox"


class User(Base):
    __tablename__ = "core_user"

    id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
        index=True
    )
    username: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(128), default='')
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_staff: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=False)
    first_name: Mapped[str] = mapped_column(String(150), default='')
    last_name: Mapped[str] = mapped_column(String(150), default='')
    home_folder_id = mapped_column(ForeignKey("core_basetreenode.id"))
    inbox_folder_id = mapped_column(ForeignKey("core_basetreenode.id"))

    date_joined: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )


class Node(Base):
    __tablename__ = "core_basetreenode"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), primary_key=True, index=True)
    lang: Mapped[str] = mapped_column(String(8), default='deu')
    ctype: Mapped[str] = mapped_column(String(16), default='folder')
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )
    user_id: Mapped["User"] = mapped_column(
        String(32),
        ForeignKey("core_user.id")
    )
    user = relationship("User", foreign_keys=[user_id])
    parent_id = mapped_column(
        "parent_id",
        String(32),
        ForeignKey("core_basetreenode.id")
    )


class Folder(Base):
    __tablename__ = "core_folder"

    column_not_exist_in_db = Column(Integer, primary_key=True)
    basetreenode_ptr_id: Mapped["Node"] = mapped_column(
        String(32),
        ForeignKey("core_basetreenode.id")
    )
    basetreenode_ptr = relationship("Node", foreign_keys=[basetreenode_ptr_id])
