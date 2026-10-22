"""Gera o Refresh Token do Google Ads via login no navegador.

Uso:
    python gerar_refresh_token.py client_secret.json

O client_secret.json é o arquivo baixado do Google Cloud (OAuth > App para computador).
"""
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/adwords"]


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python gerar_refresh_token.py client_secret.json")
    flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1], scopes=SCOPES)
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    print("\nCole estes valores no google-ads.yaml:\n")
    print(f"client_id: {creds.client_id}")
    print(f"client_secret: {creds.client_secret}")
    print(f"refresh_token: {creds.refresh_token}")


if __name__ == "__main__":
    main()
