import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(
    "https://api.mailersend.com/v1/domains",
    headers={
        "Authorization": "Bearer mlsn.22b9a810efe9a19facb84d3946cbfb552b80f8161e32b79923175478083347b5",
        "Content-Type": "application/json"
    }
)

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode()}")
