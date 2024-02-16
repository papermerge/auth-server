from enum import Enum

from .google import GoogleAuth
from .github import GithubAuth
from .ldap import LDAPAuth


class AuthProvider(str, Enum):
    GOOGLE = "google"
    GITHUB = "github"
    LDAP = "ldap"
