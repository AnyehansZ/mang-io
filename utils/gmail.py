import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from mailparser import parse_from_bytes

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_gmail_service(credentials_path='credentials.json', token_path='token.json'):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


def clean_sender(sender_raw):
    if not sender_raw:
        return 'Unknown sender'
    if isinstance(sender_raw, tuple):
        return f"{sender_raw[0]} <{sender_raw[1]}>"
    if isinstance(sender_raw, list):
        if len(sender_raw) > 0 and isinstance(sender_raw[0], tuple):
            return f"{sender_raw[0][0]} <{sender_raw[0][1]}>"
        return str(sender_raw)
    return str(sender_raw)


def clean_body(body_raw):
    if isinstance(body_raw, list):
        return ' '.join(body_raw)
    return body_raw or ''


def fetch_emails(service, max_results=5, min_body_length=0, show_progress=False):
    results = service.users().messages().list(
        userId='me', maxResults=max_results
    ).execute()
    messages = results.get('messages', [])
    if not messages:
        return []

    emails = []
    for i, msg in enumerate(messages, 1):
        if show_progress:
            print(f"  Downloading email {i}/{len(messages)}...", end='\r')

        mail = service.users().messages().get(
            userId='me', id=msg['id'], format='raw'
        ).execute()
        raw_data = base64.urlsafe_b64decode(mail['raw'])
        parsed = parse_from_bytes(raw_data)

        body = clean_body(parsed.text_plain or parsed.text_html or '')
        if min_body_length and len(body.strip()) < min_body_length:
            continue

        emails.append({
            'id': msg['id'],
            'subject': parsed.subject or '(No subject)',
            'sender': clean_sender(parsed.from_),
            'date': str(parsed.date) if parsed.date else 'Unknown date',
            'body': body,
        })

    if show_progress:
        print(f"\n  Done. {len(emails)} emails kept.\n")

    return emails