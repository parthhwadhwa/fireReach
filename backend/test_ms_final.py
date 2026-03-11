from mailersend import MailerSendClient
from mailersend.models.email import EmailRequest, EmailContact

client = MailerSendClient("mlsn.22b9a810efe9a19facb84d3946cbfb552b80f8161e32b79923175478083347b5")
req = EmailRequest(
    from_email=EmailContact(email="info@test-vz9dlem9y6p4kj50.mlsender.net", name="FireReach Agent"),
    to=[EmailContact(email="parthwadhwa15@gmail.com", name="Parth")],
    subject="Final test",
    text="Test",
    html="<p>Test</p>"
)
print("Sending test...")
resp = client.emails.send(req)
print("Response:", resp)
