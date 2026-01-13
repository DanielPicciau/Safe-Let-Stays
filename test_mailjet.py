import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(env_path)

print("...Loading Mailjet Test Script...")
import base64
from mailjet_rest import Client

# --- CONFIGURATION ---
# Replace these with your ACTUAL keys if running locally
API_KEY = os.environ.get('MAILJET_API_KEY', 'YOUR_API_KEY_HERE')
API_SECRET = os.environ.get('MAILJET_API_SECRET', 'YOUR_SECRET_KEY_HERE')
SENDER_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'daniel@webflare.studio')
RECIPIENT_EMAIL = 'danieljunior.business@gmail.com' # Change if needed

def test_mailjet():
    print("🚀 Starting Mailjet API Test...")
    print(f"   API Key: {API_KEY[:4]}...{API_KEY[-4:] if len(API_KEY) > 8 else '****'}")
    print(f"   Sender: {SENDER_EMAIL}")
    print(f"   Recipient: {RECIPIENT_EMAIL}")

    if 'YOUR_API_KEY' in API_KEY:
        print("❌ ERROR: You must set your API Key and Secret in the script or environment variables.")
        return

    try:
        mailjet = Client(auth=(API_KEY, API_SECRET), version='v3.1')
        
        data = {
          'Messages': [
            {
              "From": {
                "Email": SENDER_EMAIL,
                "Name": "Safe Let Stays Test"
              },
              "To": [
                {
                  "Email": RECIPIENT_EMAIL,
                  "Name": "Test User"
                }
              ],
              "Subject": "Mailjet API Test - Safe Let Stays",
              "TextPart": "This is a test email from the Mailjet API integration script.",
              "HTMLPart": "<h3>Mailjet Test</h3><p>If you see this, the API connection is working!</p>"
            }
          ]
        }
        
        print("   Sending request...")
        result = mailjet.send.create(data=data)
        
        print(f"   Status Code: {result.status_code}")
        print(f"   Response: {result.json()}")
        
        if result.status_code == 200:
            print("✅ SUCCESS: Email sent successfully!")
        else:
            print("❌ FAILURE: Mailjet returned an error.")

    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    test_mailjet()
