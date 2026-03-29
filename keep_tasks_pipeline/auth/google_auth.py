"""Google OAuth2 authentication helper."""

import json
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config import CREDENTIALS_PATH, GOOGLE_SCOPES, TOKEN_PATH


def get_google_credentials() -> Credentials:
    """Return valid Google credentials, prompting OAuth flow if needed."""
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, GOOGLE_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"Google credentials not found at {CREDENTIALS_PATH}\n"
                    "Download credentials.json from Google Cloud Console:\n"
                    "  https://console.cloud.google.com/apis/credentials\n"
                    "Enable 'Google Tasks API' and create an OAuth 2.0 Client ID."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, GOOGLE_SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return creds
