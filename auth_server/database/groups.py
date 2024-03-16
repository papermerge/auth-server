from sqlalchemy import select
from sqlalchemy.orm import Session

from auth_server import schemas
from auth_server.database import models


def create_group(
    session: Session,
    name: str,
    scopes: list[str],
) -> schemas.Group:

    stmt = select(models.Permission).where(
        models.Permission.codename.in_(scopes)
    )
    perms = session.execute(stmt).scalars().all()
    group = models.Group(
        name=name,
        permissions=perms
    )
    session.add(group)
    session.commit()
    result = schemas.Group.model_validate(group)

    return result

