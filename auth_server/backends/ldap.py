import logging


logger = logging.getLogger(__name__)


class LDAPAuth:
    name: str = 'ldap'
    access_token: str | None = None
