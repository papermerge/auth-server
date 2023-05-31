from enum import Enum

from .google import GoogleAuth


class OAuth2Provider(str, Enum):
    GOOGLE = "google"
    GITHUB = "github"
