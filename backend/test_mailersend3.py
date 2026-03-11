import os
from mailersend import emails

mailer = emails.NewEmail("mlsn.22b9a810efe9a19facb84d3946cbfb552b80f8161e32b79923175478083347b5")
mail_body = {}
mail_from = {"name": "Test", "email": "info@test-vz9dlem9y6p4kj50.mlsender.net"}
recipients = [{"name": "Parth", "email": "parthwadhwa15@gmail.com"}]
mailer.set_mail_from(mail_from, mail_body)
mailer.set_mail_to(recipients, mail_body)
mailer.set_subject("Test", mail_body)
mailer.set_plaintext_content("Test", mail_body)
print(mailer.send(mail_body))
