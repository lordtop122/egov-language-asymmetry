import json
from playwright.sync_api import sync_playwright

def show(req):
    if req.method != "POST":
        return
    try:
        pl = json.loads(req.post_data)[0]
        print("ROUTE:", pl["route"]["url"], "| params:",
              json.dumps(pl.get("queryParams"), ensure_ascii=False))
    except Exception:
        print("POST (unparsed):", (req.post_data or "")[:150])

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(locale="ru-RU")
    page.on("request", show)

    print("--- loading family page ---")
    page.goto("https://egov.kz/ru/navigation/family", wait_until="networkidle")
    page.wait_for_timeout(3000)

    print("--- clicking Здравоохранение ---")
    page.get_by_text("Здравоохранение", exact=True).first.click()
    page.wait_for_timeout(4000)
    print("URL now:", page.url)

    input("Press Enter to close the browser...")
    browser.close()