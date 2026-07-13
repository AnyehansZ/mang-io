from utils.gmail import get_gmail_service, fetch_emails


def main():
    print("Connecting to Gmail...")
    service = get_gmail_service()

    print("Fetching emails...")
    emails = fetch_emails(service, max_results=5)

    if not emails:
        print("No emails found in inbox.")
        return

    print(f"\nYour {len(emails)} most recent emails:\n")
    for i, email in enumerate(emails, 1):
        body_preview = email['body'][:200]
        if len(email['body']) > 200:
            body_preview += "..."
        print(f"--- Email {i} ---")
        print(f"Subject: {email['subject']}")
        print(f"From:    {email['sender']}")
        print(f"Date:    {email['date']}")
        print(f"Preview: {body_preview}")
        print()


if __name__ == '__main__':
    main()