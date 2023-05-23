from sqlalchemy.orm import Session

from . import models


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(
        models.User
    ).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user_from_email(db: Session, email: str):
    # 0. generate 3 UUIDs (one for user, one for home and one for inbox folders)
    # 1. create user (INSERT into core_users)
    # 2. create node instance (INSERT INTO core_basetreenode) x2
    # 3. create folder instance (INSERT INTO core_folder) - home and inbox!
    # 4. update user's home_folder_id and inbox_folder_id
    # Perform four steps (1., 2., 3., 4.) in one single DB transaction!
    pass
