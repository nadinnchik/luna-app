import urllib.request
import json
import ssl
import os

for k in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"]:
    if k in os.environ:
        del os.environ[k]

ctx = ssl._create_unverified_context()
opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({}),
    urllib.request.HTTPSHandler(context=ctx)
)

with open("/Users/vi/.openclaw/workspace-wife/luna-webapp/index_standalone.html", "r", encoding="utf-8") as f:
    html_data = f.read()

# Try uploading to a clean free static hosting / hastebin / github gist / pastebin / netlify / cloudflare
print("HTML ready, size:", len(html_data))
