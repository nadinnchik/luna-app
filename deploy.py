import urllib.request
import json
import base64
import os
import ssl

for k in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"]:
    if k in os.environ:
        del os.environ[k]

ctx = ssl._create_unverified_context()
opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({}),
    urllib.request.HTTPSHandler(context=ctx)
)

# Read HTML and Avatar
with open("/Users/vi/.openclaw/workspace-wife/preview/luna_perfect.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Inline the avatar image as base64 so it works anywhere without external asset loading
with open("/Users/vi/.openclaw/workspace-wife/preview/luna_avatar.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

html_inlined = html_content.replace('src="luna_avatar.jpg"', f'src="data:image/jpeg;base64,{img_b64}"')

# Also add Telegram WebApp JS SDK
tg_sdk = '<script src="https://telegram.org/js/telegram-web-app.js"></script><script>window.Telegram.WebApp.ready();window.Telegram.WebApp.expand();</script>'
html_inlined = html_inlined.replace('</head>', f'{tg_sdk}</head>')

with open("/Users/vi/.openclaw/workspace-wife/luna-webapp/index_standalone.html", "w", encoding="utf-8") as f:
    f.write(html_inlined)

print("Inlined standalone HTML created! Size:", len(html_inlined))
