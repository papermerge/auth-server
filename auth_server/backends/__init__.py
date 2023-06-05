from enum import Enum

from .google import GoogleAuth
from .github import GithubAuth


class OAuth2Provider(str, Enum):
    GOOGLE = "google"
    GITHUB = "github"
