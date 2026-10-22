import subprocess
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import shlex

FILE = "instagram.html"

def clickSelector(selector, page):
  page.locator(selector).first.click()

def scrollDownSelector(selector, page, delay=500):
  scrollbox = page.locator(selector).first
  scrollbox.wait_for(state="visible")

  unchanged = 0
  previous = None

  while True: 
    scrollbox.hover()
    page.mouse.wheel(0, 800)
    page.wait_for_timeout(delay)
    current = scrollbox.evaluate("""
      el => [el.scrollTop, el.scrollHeight]
    """)

    print(current)

    if current == previous:
      unchanged += 1
    else:
      unchanged = 0
    if unchanged >= 5:
      print("Reached bottom")
      break
    previous = current

def extractHTML(page, selector):
  html = page.locator(selector).first.inner_html()
  with open(FILE, "w", encoding="utf-8") as f:
    f.write(html)
  return html

def generateReport():
  Path("reports").mkdir(exist_ok=True)
  date = datetime.now(ZoneInfo("Europe/Madrid")).strftime("%Y-%m-%d")
  output = f"reports/{date}.txt"
  if Path(output).exists():
    Path(FILE).unlink(missing_ok=True)
    print(f"Report already exists: {output}")
    return output
  command = (
    f"grep -oE 'href=\"/[^/]+/\"' {shlex.quote(FILE)} "
    "| cut -d '\"' -f2 "
    "| tr -d '/' "
    f"| sort -u > {shlex.quote(output)}"
  )
  subprocess.run(
    command,
    shell=True,
    executable="/bin/bash",
    check=True
  )
  Path(FILE).unlink(missing_ok=True)
  print(f"Report saved to {output}")
  return output
  

def loop(page, selector_list, delay=500):
  clickSelector(selector_list[0], page)
  scrollDownSelector(
    selector_list[1],
    page,
    delay
  )
  extractHTML(page, selector_list[1])
  report = generateReport()
  return report
