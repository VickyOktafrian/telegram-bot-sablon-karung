#!/usr/bin/env python3
"""
Bersihkan export workflow n8n sebelum dipublikasikan ke GitHub.

Yang dilakukan:
  1. Hapus blok "credentials" di semua node (ID kredensial Telegram/Google/Groq).
  2. Ganti token bot Telegram yang tertanam di URL dengan placeholder.
  3. Ganti ID Google Sheet (di parameter maupun di URL/kode) dengan placeholder.
  4. Hapus ID unik instance (instanceId, id workflow, versionId, webhookId).
  5. Pindai hasil akhir untuk pola rahasia yang masih tersisa.

Pemakaian:
  python scripts/sanitize_workflow.py workflow-mentah.json workflow/bot-telegram-sablon-karung.json

PENTING: jangan pernah commit file mentah hasil ekspor n8n. Simpan di luar repo.
"""
import json
import re
import sys
from pathlib import Path

SHEET_PLACEHOLDER = "YOUR_GOOGLE_SHEET_ID"
TOKEN_PLACEHOLDER = "YOUR_TELEGRAM_BOT_TOKEN"

BOT_TOKEN_IN_URL = re.compile(r"bot\d{6,}:[A-Za-z0-9_-]{30,}")
SHEET_IN_URL = re.compile(r"spreadsheets/d/([A-Za-z0-9_-]{25,})")

LEAK_PATTERNS = {
    "Token bot Telegram": r"\d{6,}:[A-Za-z0-9_-]{30,}",
    "API key Groq": r"gsk_[A-Za-z0-9]{20,}",
    "API key Google": r"AIza[0-9A-Za-z_-]{30,}",
    "API key gaya OpenAI": r"sk-[A-Za-z0-9]{20,}",
    "Bearer token": r"Bearer\s+[A-Za-z0-9._-]{20,}",
}


def collect_sheet_ids(obj, found):
    """Kumpulkan semua ID Google Sheet yang muncul di workflow."""
    if isinstance(obj, dict):
        doc = obj.get("documentId")
        if isinstance(doc, dict) and isinstance(doc.get("value"), str):
            found.add(doc["value"])
        for v in obj.values():
            collect_sheet_ids(v, found)
    elif isinstance(obj, list):
        for v in obj:
            collect_sheet_ids(v, found)
    elif isinstance(obj, str):
        found.update(SHEET_IN_URL.findall(obj))


def main(src, dst):
    data = json.loads(Path(src).read_text(encoding="utf-8"))

    # 1 & 4: kredensial dan ID unik instance
    for node in data.get("nodes", []):
        node.pop("credentials", None)
        node.pop("webhookId", None)
    for key in ("id", "versionId", "meta"):
        data.pop(key, None)
    data["pinData"] = {}
    data["active"] = False

    # 3: kumpulkan ID sheet sebelum diganti
    sheet_ids = set()
    collect_sheet_ids(data, sheet_ids)

    text = json.dumps(data, ensure_ascii=False, indent=2)

    # 2: token bot
    text, n_token = BOT_TOKEN_IN_URL.subn("bot" + TOKEN_PLACEHOLDER, text)

    # 3: ID sheet
    n_sheet = 0
    for sid in sheet_ids:
        n_sheet += text.count(sid)
        text = text.replace(sid, SHEET_PLACEHOLDER)

    # 5: pindai sisa rahasia
    problems = []
    for label, pattern in LEAK_PATTERNS.items():
        if re.search(pattern, text):
            problems.append(label)

    json.loads(text)  # pastikan JSON masih valid
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    Path(dst).write_text(text, encoding="utf-8")

    print(f"Selesai -> {dst}")
    print(f"  token bot diganti      : {n_token}")
    print(f"  ID sheet diganti       : {n_sheet}")
    if problems:
        print("  PERINGATAN, masih terdeteksi:", ", ".join(problems))
        sys.exit(1)
    print("  pemindaian rahasia     : bersih")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
