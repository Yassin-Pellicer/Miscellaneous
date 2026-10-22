Set your own WhatsApp number with country code (digits only):

```bash
export WHATSAPP_PHONE='34603786942'
```

Link WhatsApp once:

```bash
python whatsapp_report.py
```

Scan the QR code using WhatsApp on your phone → Linked devices → Link a device. The window closes automatically once logged in. Login is saved in `whatsapp_chrome_profile`.

Then run normally:

```bash
python launch_profile.py INSTAGRAM_USERNAME
```

After creating the daily report, the script sends new followers and accounts no longer listed compared with yesterday to the configured number. If yesterday's report is missing, it only saves today's baseline. It sends a message on every run with a yesterday report, even if there are no changes. Runs are not scheduled automatically.

After linking, optionally hide the WhatsApp window:

```bash
export WHATSAPP_HEADLESS=1
```

If the session expires, unset `WHATSAPP_HEADLESS` and run `python whatsapp_report.py` again. Instagram remains headless. Email settings are no longer used by the main script. WhatsApp Web selectors may need updating if its interface changes.
