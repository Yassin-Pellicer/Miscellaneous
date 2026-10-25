import argparse
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import shutil
import subprocess

from playwright.sync_api import sync_playwright # type: ignore
from interaction import loop, report_path
from whatsapp_report import send_difference

from steps import check_followers_flow, check_following_flow

PROFILE = str(Path(__file__).resolve().parent / "instagram_chrome_profile")

def argument_parser():
  """
  Create an argument parser for the Instagram profile launcher.

  Returns:
    argparse.ArgumentParser: The configured argument parser.
  """
  parser = argparse.ArgumentParser()

  parser.add_argument("username", nargs="?")
  parser.add_argument("--setup", action="store_true", help="Open regular Chrome without Playwright")
  parser.add_argument("--followers", action="store_true", help="Check followers instead of following")
  parser.add_argument("--following", action="store_true", help="Check following instead of followers")
  return parser

def main():
  """
  Main function to launch the Instagram profile.

  """
  parser = argument_parser()
  args = parser.parse_args()

  if not args.username and not args.setup:
    parser.error("username is required unless using --setup")

  # Determine the URL to open based on the provided username or default to Instagram's homepage.
  url = f"https://www.instagram.com/{args.username.strip('@/')}/" if args.username else "https://www.instagram.com/"

  # Setup Step
  if args.setup:
    chrome = shutil.which("google-chrome") or shutil.which("google-chrome-stable")
    if not chrome:
      parser.error("Google Chrome is not installed")
    print("Log in and complete verification, then close Chrome before running automation.", flush=True)
    subprocess.run(
      [chrome, f"--user-data-dir={PROFILE}", "--profile-directory=Default", url],
      check=True,
    )
    return

  day = datetime.now(ZoneInfo("Europe/Madrid")).date()
  report_type = "following" if args.following else "followers"

  report = report_path(report_type, day)
  followers_report = report_path("followers", day) if args.following else None

  with sync_playwright() as p:
    if not report.is_file() or (followers_report and not followers_report.is_file()):
      context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE,
        channel="chrome",
        headless=False,
        ignore_default_args=["--password-store=basic", "--use-mock-keychain"],
        args=["--profile-directory=Default"],
        locale="en-US"
      )
      try:
        page = context.pages[0] if context.pages else context.new_page()
        if not report.is_file():
          page.goto(url)
          selectors = check_following_flow if args.following else check_followers_flow
          loop(page, selectors, report_type=report_type, day=day)
        else:
          print(f"Report already exists: {report}")

        if followers_report and not followers_report.is_file():
          page.goto(url)
          loop(page, check_followers_flow, report_type="followers", day=day)

      finally:
        context.close()

    send_difference(
      report, p,
      followers_report=followers_report,
      report_type=report_type,
    )


if __name__ == "__main__":
  main()
