#!/usr/bin/env python3
import os
import sys
import json
import base64
import time
import urllib.request

TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "nadinnchik/luna-app"
BRANCH = "main"
BASE_DIR = "/Users/nadinn/Documents/Luna"


def api_request(endpoint, method="GET", data_dict=None):
    url = endpoint if endpoint.startswith("http") else f"https://api.github.com/repos/{REPO}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "User-Agent": "Luna-Deploy-Bot",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    data_bytes = json.dumps(data_dict).encode("utf-8") if data_dict is not None else None
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def create_blob(file_path):
    with open(file_path, "rb") as f:
        b64_content = base64.b64encode(f.read()).decode("utf-8")
    resp = api_request("git/blobs", method="POST", data_dict={
        "content": b64_content,
        "encoding": "base64"
    })
    return resp["sha"]


def deploy():
    print(f"🚀 Deploying all updates to GitHub ({REPO}:{BRANCH})...")

    # 1. Get latest commit and base tree
    ref_data = api_request(f"git/ref/heads/{BRANCH}")
    latest_commit_sha = ref_data["object"]["sha"]
    commit_data = api_request(f"git/commits/{latest_commit_sha}")
    base_tree_sha = commit_data["tree"]["sha"]
    print(f"📌 Base Tree SHA: {base_tree_sha[:8]}")

    # 2. Files to upload
    files_to_sync = [
        "index.html",
        "index_standalone.html",
        "bot/bot_runner.py",
        "bot/set_menu_button.py",
        "Dockerfile",
        "Procfile",
        "railway.json",
        "requirements.txt",
        "README.md",
        "server/Dockerfile",
        "server/Procfile",
        "server/railway.json",
        "server/requirements.txt",
        "server/test_all.py",
        "server/test_auth.py",
        "server/app/main.py",
        "server/app/database.py",
        "server/app/core/config.py",
        "server/app/core/telegram_auth.py",
        "server/app/core/deps.py",
        "server/app/models/models.py",
        "server/app/schemas/schemas.py",
        "server/app/api/v1/api.py",
        "server/app/api/v1/endpoints/auth.py",
        "server/app/api/v1/endpoints/profile.py",
        "server/app/api/v1/endpoints/children.py",
        "server/app/api/v1/endpoints/quiz.py",
        "server/app/api/v1/endpoints/analytics.py",
        "server/app/api/v1/endpoints/chat.py",
    ]

    tree_items = []
    for rel in files_to_sync:
        abs_p = os.path.join(BASE_DIR, rel)
        if os.path.exists(abs_p):
            print(f"  ⬆️ Uploading blob: {rel}...")
            sha = create_blob(abs_p)
            tree_items.append({
                "path": rel,
                "mode": "100644",
                "type": "blob",
                "sha": sha
            })

    # 3. Create tree
    print("🌲 Creating new Git tree...")
    tree_resp = api_request("git/trees", method="POST", data_dict={
        "base_tree": base_tree_sha,
        "tree": tree_items
    })
    new_tree_sha = tree_resp["sha"]

    # 4. Create commit
    commit_msg = "feat: upgrade LUNA PRO to full 37-chapter personalized book engine with 7 core blocks and luxury PDF export"
    print(f"📝 Creating commit: '{commit_msg}'...")
    commit_resp = api_request("git/commits", method="POST", data_dict={
        "message": commit_msg,
        "tree": new_tree_sha,
        "parents": [latest_commit_sha]
    })
    new_commit_sha = commit_resp["sha"]

    # 5. Update branch reference
    print(f"🔄 Updating {BRANCH} branch to commit {new_commit_sha[:8]}...")
    api_request(f"git/refs/heads/{BRANCH}", method="PATCH", data_dict={
        "sha": new_commit_sha,
        "force": True
    })

    print(f"\n✨ ALL UPDATES DEPLOYED SUCCESSFULLY!")
    print(f"🌐 Live WebApp URL: https://nadinnchik.github.io/luna-app/")


if __name__ == "__main__":
    deploy()
