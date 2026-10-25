# Instagram reports with WhatsApp notifications

Save daily Instagram followers and following lists, compare followers with the previous recorded day, and send results to your own WhatsApp number.

## Requirements

- Python 3.9 or newer with Playwright installed: `python -m pip install playwright`.
- Google Chrome available as `google-chrome` or `google-chrome-stable`.
- A desktop session to display browser windows.
- Bash at `/bin/bash`, plus `grep`, `cut`, `tr`, and `sort` for extracting reports.

Run commands from this project directory. Reports are saved relative to the working directory; browser sessions are saved beside the scripts.

## One-time setup

### Instagram

```bash
python launch_profile.py --setup
```

Sign in manually, complete any verification, then close Chrome normally before running automation. Setup opens regular Chrome. Setup and automation share `instagram_chrome_profile`, its `Default` profile, and Chrome's normal credential store.

If Instagram asks you to log in again, rerun setup. If Instagram rejects your login during setup, check whether you can sign in manually in your usual browser too.

### WhatsApp

Edit `WHATSAPP_PHONE` near the top of `whatsapp_report.py` to your own number, including country code and digits only:

```python
WHATSAPP_PHONE = "34123456789"  # Replace with your own number.
```

The code reads this constant directly. Setting a `WHATSAPP_PHONE` environment variable does not change the recipient.

Link WhatsApp once:

```bash
python whatsapp_report.py
```

On your phone, open **WhatsApp → Linked devices → Link a device** and scan the QR code. The browser closes automatically when the chat list loads. Login is saved in `whatsapp_chrome_profile`. Rerun this command if the session expires.

## Followers changes

```bash
python launch_profile.py INSTAGRAM_USERNAME
# Equivalent:
python launch_profile.py INSTAGRAM_USERNAME --followers
```

The script collects today's followers if their report is missing, then compares them with the most recent earlier report in `reports/followers/`. That report does not have to be from yesterday.

The WhatsApp message includes the follower count, net change, sorted additions marked `(+)`, and sorted removals marked `(-)`. Without an earlier report, today's list becomes the baseline and no message is sent.

## Accounts that do not follow you back

```bash
python launch_profile.py INSTAGRAM_USERNAME --following
```

The script collects today's following list if missing, then today's followers if missing. It sends the sorted result of **following minus followers**, with the total following count and the number of accounts that do not follow you back. This works on the first recorded day and needs no earlier report.

Use one option per command. If both `--followers` and `--following` are supplied, the current code uses `--following`.

## Daily reports and reuse

```text
reports/
  followers/
    YYYY-MM-DD_followers.txt
  following/
    YYYY-MM-DD_following.txt
```

Each file contains sorted, unique account names, one per line. Dates use the `Europe/Madrid` timezone.

- An existing report for today skips scraping that list and is not overwritten.
- With `--following`, only missing lists are collected.
- If all required reports exist, Instagram does not open. The saved reports are still used to build and send the WhatsApp message.
- Followers messages are sent on every run with an earlier report, even if nothing changed. Following messages are also sent on repeated runs.
- To refresh a list on the same day, move its report elsewhere before rerunning the command.

Reports are shared by date and list type, without an account name in the path. Use a separate project copy per Instagram account to avoid mixing reports and sessions. Older reports outside these directories are not found automatically. Within the followers directory, the comparison accepts both `YYYY-MM-DD.txt` and suffixed filenames.

## Browser behavior and troubleshooting

Instagram automation and WhatsApp currently use visible browser windows. `WHATSAPP_HEADLESS` is not read by the code, so exporting it has no effect. Instagram uses English browser locale because the selectors match `followers` and `following`.

Close setup windows before automation and avoid simultaneous runs sharing a browser profile. If WhatsApp needs verification while sending, its visible window allows QR scanning; the script waits up to three minutes for the message composer. Long messages are split into chunks of up to 3,000 characters.

If an interface change breaks scraping or sending, check the Instagram selectors in `steps.py` and WhatsApp selectors in `whatsapp_report.py`.

Runs are manual; the project does not schedule them automatically.
