import os
import re
from datetime import date
from pathlib import Path

from playwright.sync_api import expect, sync_playwright # type: ignore

PROFILE = str(Path(__file__).parent / "whatsapp_chrome_profile")
WHATSAPP_PHONE = "34603786942"  # Set your own number including country code, digits only. Example: "34600123456"

def report_date(report):
  return date.fromisoformat(Path(report).stem.split("_", 1)[0])

def read_accounts(report):
  return set(Path(report).read_text(encoding="utf-8").splitlines()) - {""}

def build_difference(report):
  today = Path(report)
  today_date = report_date(today)
  earlier_reports = []

  for candidate in today.parent.glob("*.txt"):
    try:
      candidate_date = report_date(candidate)
    except ValueError:
      continue
    if candidate.is_file() and candidate_date < today_date:
      earlier_reports.append((candidate_date, candidate))

  if not earlier_reports:
    print("Baseline saved; no earlier report available.")
    return None

  previous_report = max(earlier_reports, key=lambda item: item[0])[1]
  current = read_accounts(today)
  previous = read_accounts(previous_report)

  lines = [f"Your followers on {today.stem} compared to {previous_report.stem} (last recorded day)."]
  lines.append(f"Followers: {len(current)} ({len(current) - len(previous):+d})")
  lines.extend(f"(+) {name}" for name in sorted(current - previous))
  lines.extend(f"(-) {name}" for name in sorted(previous - current))
  return "\n".join(lines)

def build_following_difference(following_report, followers_report):
  following = read_accounts(following_report)
  followers = read_accounts(followers_report)
  difference = following - followers

  lines = [f"Accounts you follow who don't follow you back on {report_date(following_report)}."]
  lines.append(f"Following: {len(following)}; not following you back: {len(difference)}")
  lines.extend(f"(-) {name}" for name in sorted(difference))
  return "\n".join(lines)

def open_whatsapp(playwright, headless=False):
  return playwright.chromium.launch_persistent_context(
    user_data_dir=PROFILE, channel="chrome", headless=headless
  )

def send_difference(report, playwright, followers_report=None, *, report_type="followers"):
  if report_type == "following":
    if followers_report is None:
      raise ValueError("A followers report is required for the following comparison.")
    text = build_following_difference(report, followers_report)
  elif report_type == "followers":
    text = build_difference(report)
  else:
    raise ValueError(f"Unknown report type: {report_type}")

  if text is None:
    return

  phone = WHATSAPP_PHONE.strip().removeprefix("+")
  if not re.fullmatch(r"[1-9][0-9]{6,14}", phone):
    raise ValueError(
      "Set WHATSAPP_PHONE to your own number including country code, digits only."
    )

  context = open_whatsapp(playwright, headless=False)
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
