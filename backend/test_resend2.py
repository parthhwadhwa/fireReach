import urllib.request
import json
import os

req = urllib.request.Request(
    "https://api.resend.com/emails",
    data=json.dumps({
        "from": "onboarding@resend.dev",
        "to": "parthwadhwa15@gmail.com",
        "subject": "Test",
        "html": "<p>Test</p>"
    }).encode("utf-8"),
    headers={
        "Authorization": "Bearer re_Ut7JYWZN_JQ9B7JQfQZXgfNVnNHVfmCNF",
        "Content-Type": "application/json"
    }
)

try:
    with urllib.request.urlopen(req) as resp:
        print(resp.read().decode())
except urllib.error.HTTPError as e:
    print(f"Code: {e.code}, body: {e.read().decode()}")
