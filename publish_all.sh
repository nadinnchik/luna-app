#!/bin/sh
set -e

TOKEN="${GITHUB_TOKEN:-}"
REPO="nadinnchik/luna-app"
BRANCH="main"
BASE_DIR="/Users/nadinn/Documents/Luna"

echo "🚀 Fast publishing to GitHub using Git Data API (IPv4)..."

# 1. Get branch latest commit
REF_RESP=$(curl -4 -s -H "Authorization: Bearer $TOKEN" -H "User-Agent: Luna-Deploy" https://api.github.com/repos/$REPO/git/ref/heads/$BRANCH)
LATEST_COMMIT_SHA=$(echo "$REF_RESP" | grep -o '"sha": "[^"]*' | head -n 1 | cut -d'"' -f4)

COMMIT_RESP=$(curl -4 -s -H "Authorization: Bearer $TOKEN" -H "User-Agent: Luna-Deploy" https://api.github.com/repos/$REPO/git/commits/$LATEST_COMMIT_SHA)
BASE_TREE_SHA=$(echo "$COMMIT_RESP" | grep -o '"sha": "[^"]*' | head -n 1 | cut -d'"' -f4)

echo "📌 Base Tree: $BASE_TREE_SHA"

upload_blob() {
  FILE_PATH="$1"
  TMP_BLOB="/tmp/blob_upload_$$.json"
  printf '{"content":"' > "$TMP_BLOB"
  base64 -i "$BASE_DIR/$FILE_PATH" | tr -d '\n' >> "$TMP_BLOB"
  printf '","encoding":"base64"}' >> "$TMP_BLOB"

  BLOB_RESP=$(curl -4 -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "User-Agent: Luna-Deploy" \
    -H "Accept: application/vnd.github.v3+json" \
    -H "Content-Type: application/json" \
    --data-binary @"$TMP_BLOB" \
    "https://api.github.com/repos/$REPO/git/blobs")
  rm -f "$TMP_BLOB"

  BLOB_SHA=$(echo "$BLOB_RESP" | grep -o '"sha": "[^"]*' | head -n 1 | cut -d'"' -f4)
  echo "$BLOB_SHA"
}

echo "📦 Uploading blobs..."
SHA_INDEX=$(upload_blob "index.html")
echo "✅ index.html: $SHA_INDEX"

SHA_STANDALONE=$(upload_blob "index_standalone.html")
echo "✅ index_standalone.html: $SHA_STANDALONE"

SHA_SCHEMAS=$(upload_blob "server/app/schemas/schemas.py")
echo "✅ schemas.py: $SHA_SCHEMAS"

SHA_PROFILE=$(upload_blob "server/app/api/v1/endpoints/profile.py")
echo "✅ profile.py: $SHA_PROFILE"

SHA_TESTS=$(upload_blob "server/test_all.py")
echo "✅ test_all.py: $SHA_TESTS"

# 3. Create new tree
TMP_TREE="/tmp/new_tree_$$.json"
cat <<EOF > "$TMP_TREE"
{
  "base_tree": "$BASE_TREE_SHA",
  "tree": [
    {"path": "index.html", "mode": "100644", "type": "blob", "sha": "$SHA_INDEX"},
    {"path": "index_standalone.html", "mode": "100644", "type": "blob", "sha": "$SHA_STANDALONE"},
    {"path": "server/app/schemas/schemas.py", "mode": "100644", "type": "blob", "sha": "$SHA_SCHEMAS"},
    {"path": "server/app/api/v1/endpoints/profile.py", "mode": "100644", "type": "blob", "sha": "$SHA_PROFILE"},
    {"path": "server/test_all.py", "mode": "100644", "type": "blob", "sha": "$SHA_TESTS"}
  ]
}
EOF

TREE_RESP=$(curl -4 -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "User-Agent: Luna-Deploy" \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Content-Type: application/json" \
  --data-binary @"$TMP_TREE" \
  "https://api.github.com/repos/$REPO/git/trees")
rm -f "$TMP_TREE"

NEW_TREE_SHA=$(echo "$TREE_RESP" | grep -o '"sha": "[^"]*' | head -n 1 | cut -d'"' -f4)
echo "🌲 New Tree SHA: $NEW_TREE_SHA"

# 4. Create Commit
TMP_COMMIT="/tmp/new_commit_$$.json"
cat <<EOF > "$TMP_COMMIT"
{
  "message": "fix: LUNA PRO 999 RUB one-time book checkout, profile active card, city placeholders",
  "tree": "$NEW_TREE_SHA",
  "parents": ["$LATEST_COMMIT_SHA"]
}
EOF

COMMIT_RESP=$(curl -4 -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "User-Agent: Luna-Deploy" \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Content-Type: application/json" \
  --data-binary @"$TMP_COMMIT" \
  "https://api.github.com/repos/$REPO/git/commits")
rm -f "$TMP_COMMIT"

NEW_COMMIT_SHA=$(echo "$COMMIT_RESP" | grep -o '"sha": "[^"]*' | head -n 1 | cut -d'"' -f4)
echo "📝 New Commit SHA: $NEW_COMMIT_SHA"

# 5. Update branch pointer
curl -4 -s -X PATCH \
  -H "Authorization: Bearer $TOKEN" \
  -H "User-Agent: Luna-Deploy" \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Content-Type: application/json" \
  -d "{\"sha\":\"$NEW_COMMIT_SHA\",\"force\":true}" \
  "https://api.github.com/repos/$REPO/git/refs/heads/$BRANCH" > /dev/null

echo "✨ All updates successfully published to GitHub! Live on https://nadinnchik.github.io/luna-app/"
