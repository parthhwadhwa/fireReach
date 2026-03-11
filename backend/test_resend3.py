import resend
import os

resend.api_key = "re_Ut7JYWZN_JQ9B7JQfQZXgfNVnNHVfmCNF"
try:
    r = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "parthwadhwa15@gmail.com",
        "subject": "Test",
        "html": "<p>Test body</p>"
    })
    print("Success:", r)
except Exception as e:
    print("Error:", e)
