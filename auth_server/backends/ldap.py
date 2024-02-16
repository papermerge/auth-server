import logging
from ldap3 import Server, Connection, ALL


logger = logging.getLogger(__name__)


class LDAPAuth:
    name: str = 'ldap'

    def __init__(self,
        url: str,
        username: str,
        password: str,
        user_dn_format: str,
        use_ssl: bool = True,
    ):
        self._username = username
        self._password = password
        self._url = url
        self._user_dn_format = user_dn_format
        self._use_ssl = use_ssl

    async def signin(self):
        server = Server(self._uri, use_ssl=self._use_ssl, get_info=ALL)
        user_dn = self._user_dn_format.format(username=self._username)
        conn = Connection(server, user_dn, self._password)

        if not conn.bind():
            # this may happen from multiple reasons:
            # 1. user simply provided wrong credentials
            # 2. auth_server configuration issues
            # 3. server side problem
            logger.warning(
                f"LDAP conn.bind() returned falsy value: {conn}"
            )
            raise Exception("LDAP conn.bind() returned falsy value")

    async def user_email(self):
        pass
