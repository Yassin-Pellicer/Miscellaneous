import argparse
from pathlib import Path
import shutil
import subprocess

PROFILE = str(Path(__file__).parent / "instagram_chrome_profile")

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("username", nargs="?")
  parser.add_argument("--setup", action="store_true", help="Open regular Chrome without Playwright")
  args = parser.parse_args()
  if not args.username and not args.setup:
    parser.error("username is required unless using --setup")
  url = f"https://www.instagram.com/{args.username.strip('@/')}/" if args.username else "https://www.instagram.com/"

  if args.setup:
    chrome = shutil.which("google-chrome") or shutil.which("google-chrome-stable")
    if not chrome:
      parser.error("Google Chrome is not installed")
    print("Log in and complete verification, then close Chrome before running automation.", flush=True)
    subprocess.run([chrome, f"--user-data-dir={PROFILE}", url], check=True)
    return

  from playwright.sync_api import sync_playwright # type: ignore
  from interaction import loop
  from whatsapp_report import send_difference

  with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
      user_data_dir=PROFILE, channel="chrome", headless=False
    )
    try:
      page = context.pages[0] if context.pages else context.new_page()
      page.goto(url)
      selector_list = [
        'a[role="link"]:has-text("seguidores")',
        'div[style*="overflow: hidden auto"]'
      ]
      report = loop(page, selector_list)
    finally:
      context.close()
    send_difference(report, p)

if __name__ == "__main__":
  main()
