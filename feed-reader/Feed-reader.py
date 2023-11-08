import os
import smtplib
import feedparser
from datetime import datetime, timedelta
import pytz

def check_feed_updates(feed_url, interval):
    feed = feedparser.parse(feed_url)

    current_date = datetime.now(pytz.utc)
    start_date = current_date - timedelta(days=interval)

    info = []  # Lijst om feed-updates op te slaan

    for entry in feed.entries:
        entry_info = {}

        if 'published' in entry:
            entry_date = datetime.fromisoformat(entry.published)
        elif 'updated' in entry:
            entry_date = datetime.fromisoformat(entry.updated)
        else:
            print("Datum/tijdstempel niet gevonden voor deze entry.")
            continue

        entry_date = entry_date.replace(tzinfo=pytz.utc)
        if entry_date >= start_date:
            entry_info['update_date'] = entry_date.strftime("%Y-%m-%d %H:%M:%S")
            entry_info['title'] = entry.title
            entry_info['summary'] = entry.summary
            entry_info['link'] = entry.link

            info.append(entry_info)

    return info

def get_urls():
    urls = [
        'https://github.com/acryldata/datahub-helm/releases.atom',
        'http://github.com/datahub-project/datahub/releases.atom'
    ]
    return urls

interval = int(os.getenv("INTERVAL_IN_DAYS", default="10"))
feed_urls = get_urls()

all_feed_updates = []  

for feed_url in feed_urls:
    feed_updates = check_feed_updates(feed_url, interval)
    all_feed_updates.extend(feed_updates)

# Stel de e-mailinhoud samen
email_subject = "Feed Updates"
email_body = ""
for update in all_feed_updates:
    email_body += f"Update found on {update['update_date']}\n"
    email_body += f"Title: {update['title']}\n"
    email_body += f"Summary: {update['summary']}\n"
    email_body += f"Link: {update['link']}\n\n"

# Verstuur de e-mail
def send_email(subject, message):
    FROM_EMAIL = os.getenv("YOUR_EMAIL")
    PASSWORD = os.getenv("YOUR_PASSWORD")
    TO_EMAIL = "tobiasvdvaart@gmail.com"  

    if FROM_EMAIL is None or PASSWORD is None:
        print("Email data not found in environment variables.")
        return

    with smtplib.SMTP("smtp.example.com", 587) as smtp:
        smtp.starttls()
        smtp.login(FROM_EMAIL, PASSWORD)

        msg = f"Subject: {subject}\n\n{message}"

        smtp.sendmail(FROM_EMAIL, TO_EMAIL, msg)

if __name__ == "__main__": 
    send_email(email_subject, email_body)