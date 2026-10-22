import os
import re
from datetime import date, timedelta
from pathlib import Path

from playwright.sync_api import expect, sync_playwright # type: ignore

PROFILE = str(Path(__file__).parent / "whatsapp_chrome_profile")

def build_difference(report):
  today = Path(report)
  yesterday = today.with_name(
    f"{date.fromisoformat(today.stem) - timedelta(days=1)}.txt"
  )
  if not yesterday.exists():
    print("Baseline saved; no report for yesterday.")
    return None
  current = set(today.read_text(encoding="utf-8").splitlines()) - {""}
  previous = set(yesterday.read_text(encoding="utf-8").splitlines()) - {""}
  lines = [f"Your followers on {today.stem} compared to {yesterday.stem} (yesterday)."]
  lines += [f"Followers: {len(current)} ({len(current) - len(previous):+d})"]
  lines += [f"(+) {name}" for name in sorted(current - previous)]
  lines += [f"(-) {name}" for name in sorted(previous - current)]
  return "\n".join(lines)

def open_whatsapp(playwright, headless=True):
  return playwright.chromium.launch_persistent_context(
    user_data_dir=PROFILE, channel="chrome", headless=headless
  )

def send_difference(report, playwright):
  text = build_difference(report)
  if text is None:
    return
  phone = os.environ.get("WHATSAPP_PHONE", "").strip().removeprefix("+")
  if not re.fullmatch(r"[1-9][0-9]{6,14}", phone):
    raise ValueError(
      "Set WHATSAPP_PHONE to your own number including country code, digits only."
    )
  context = open_whatsapp(playwright, headless=True)
  try:
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(f"https://web.whatsapp.com/send?phone={phone}")
    print("Waiting for WhatsApp; scan QR if needed.", flush=True)
    composer = page.locator('footer [contenteditable="true"][role="textbox"]').first
    composer.wait_for(state="visible", timeout=180000)
    for offset in range(0, len(text), 3000):
      chunk = text[offset : offset + 3000]
      composer.fill(chunk)
      composer.press("Enter")
      expect(composer).to_have_text("", timeout=15000)
      outgoing = page.locator(".message-out").filter(has_text=chunk).last
      outgoing.wait_for(state="visible", timeout=15000)
      outgoing.locator(
        '[data-icon="msg-check"], [data-icon="msg-dblcheck"]'
      ).first.wait_for(state="visible", timeout=30000)
    print("WhatsApp difference sent.")
  finally:
    context.close()

if __name__ == "__main__":
  with sync_playwright() as p:
    context = open_whatsapp(p)
    try:
      page = context.pages[0] if context.pages else context.new_page()
      page.goto("https://web.whatsapp.com/")
      print("Scan the QR code with WhatsApp → Linked devices.", flush=True)
      page.locator("#pane-side").wait_for(state="visible", timeout=180000)
      print("WhatsApp login saved. You can now run launch_profile.py.")
    finally:
      context.close()
