import time
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from utils.gmail import get_gmail_service, fetch_emails


def load_summarizer():
    print("Loading summarization model...")
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
    model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
    print("Model ready.\n")
    return tokenizer, model


def summarize(text, tokenizer, model, max_length=100, min_length=70):
    inputs = tokenizer(text[:1024], return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(
        inputs["input_ids"], max_length=max_length, min_length=min_length, do_sample=False
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)


def main():
    print("Fetching emails from Gmail...")
    service = get_gmail_service()
    start = time.time()
    emails = fetch_emails(service, max_results=5, min_body_length=50)
    print(f"Fetching: {time.time() - start:.1f}s")
    if not emails:
        print("No emails with enough content found.")
        return

    start = time.time()
    tokenizer, model = load_summarizer()
    print(f"Loading model: {time.time() - start:.1f}s")

    print(f"\n{'='*60}\nYOUR INBOX SUMMARY — {len(emails)} emails\n{'='*60}\n")
    for i, email in enumerate(emails, 1):
        start = time.time()
        summary = summarize(email['body'], tokenizer, model)
        print(f"📧 {i}. {email['subject']}")
        print(f"   From: {email['sender']}")
        print(f"   Summary: {summary}")
        print()
        print(f"Summarizing time: {time.time() - start:.1f}s")


if __name__ == '__main__':
    main()