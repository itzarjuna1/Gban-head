#!/bin/bash

echo "======================================"
echo "   🔥 GBAN NETWORK BOT STARTING 🔥"
echo "======================================"

# Required env vars
REQUIRED_VARS=(
  API_ID
  API_HASH
  BOT_TOKEN
  MONGO_URI
  DB_NAME
  OWNER_ID
)

echo "[INFO] Checking environment variables..."

for VAR in "${REQUIRED_VARS[@]}"; do
  if [[ -z "${!VAR}" ]]; then
    echo "[ERROR] Missing environment variable: $VAR"
    exit 1
  fi
done

echo "[INFO] All required variables found ✅"
echo "[INFO] Starting bot..."

python3 bot.py
