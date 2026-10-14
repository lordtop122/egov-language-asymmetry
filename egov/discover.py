import json, time
from playwright.sync_api import sync_playwright

CATS = ["agriculture", "citizenship", "consularServices", "culture", "customsAndTaxes",
        "development", "ecology", "education", "employment", "estate", "family",
        "finance", "health", "legalAssistance", "license", "logistics", "medicine",
        "militaryRegistration", "property", "registry", "socialWelfare", "tax", "transport"]

def parse_flight(b: bytes) -> dict:
    rows, i = {}, 0
    while i < len(b):
        colon = b.index(b":", i)
        rid = b[i:colon].decode().strip()
        j = colon + 1
        if b[j:j+1] == b"T":
            comma = b.index(b",", j)
            n = int(b[j+1:comma], 16)
            start = comma + 1
            rows[rid] = b[start:start+n].decode("utf-8")
            i = start + n
        else:
            nl = b.find(b"\n", j)
            nl = len(b) if nl == -1 else nl
            rows[rid] = b[j:nl].decode("utf-8")
            i = nl + 1
    return rows

found, routes = {}, set()

def on_response(resp):
    req = resp.request
    if req.method != "POST":
        return
    try:
        payload = json.loads(req.post_data or "")[0]
        route = payload["route"]["url"]
    except Exception:
        return
    routes.add(route)
    if not route.endswith("by-category"):
        return
    try:
        rows = parse_flight(resp.body())
        data = json.loads(rows["1"]).get("data", {})
    except Exception:
        return
    qp = payload.get("queryParams") or {}
    sub = qp.get("subcategoryId") or data.get("resolved_subcategory_id")
    key = f'{qp.get("categoryId")}|{sub}'
    found[key] = {
        "page": req.headers.get("referer") or resp.url,
        "items": [(i["service_code"], i["title"]["ru"]) for i in data.get("items", [])],
    }

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.on("response", on_response)
    for n, cat in enumerate(CATS):
        page.goto(f"https://egov.kz/ru/navigation/{cat}", wait_until="networkidle")
        page.wait_for_timeout(1500)
        if n == 0:   
            texts = page.locator("button, [role=tab], a").all_inner_texts()
            print("CLICKABLES:", [t.strip() for t in texts if t.strip()][:80])
        time.sleep(1)  
    browser.close()

print("ROUTES SEEN:", sorted(routes))
print("category/subcategory pairs found:", len(found))
print("total service entries:", sum(len(v["items"]) for v in found.values()))
with open("egov/categories_found.json", "w", encoding="utf-8") as f:
    json.dump(found, f, ensure_ascii=False, indent=1)