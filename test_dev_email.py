#!/usr/bin/env python
"""Test email delivery in development"""
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / '.env')

import os
from mailjet_rest import Client

api_key = os.environ.get('MAILJET_API_KEY')
api_secret = os.environ.get('MAILJET_API_SECRET')

mailjet = Client(auth=(api_key, api_secret), version='v3.1')

# Send to YOUR verified email
data = {
    'Messages': [{
        'From': {'Email': 'daniel@webflare.studio', 'Name': 'Safe Let Stays Test'},
        'To': [{'Email': 'daniel@webflare.studio', 'Name': 'Test User'}],
        'Subject': 'Development Test Email',
        'TextPart': 'This is a test email for development.',
        'HTMLPart': '<h3>Dev Test</h3><p>If you see this, emails are working!</p>'
    }]
}

print("Sending test email to daniel@webflare.studio...")
result = mailjet.send.create(data=data)
print(f'Status: {result.status_code}')
print(f'Response: {result.json()}')

if result.status_code == 200:
    msg_id = result.json()['Messages'][0]['To'][0]['MessageID']
    print(f"\nChecking message status...")
    
    # Check status
    mailjet_v3 = Client(auth=(api_key, api_secret), version='v3')
    status = mailjet_v3.message.get(id=msg_id)
    print(f"Message status: {status.json()['Data'][0]['Status']}")
