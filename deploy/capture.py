# Captures screenshots of the deployed Streamlit app at its forwarded URL.
import sys, time
from playwright.sync_api import sync_playwright
url, ev = sys.argv[1], sys.argv[2]
def pick(page, label, option):
    box = page.locator('div[data-testid="stSelectbox"]').filter(has_text=label).first
    box.locator('div[data-baseweb="select"]').click()
    page.get_by_role("option", name=option, exact=True).click()
    time.sleep(0.6)
with sync_playwright() as p:
    import os
    b = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
    page = b.new_page(viewport={"width": 1100, "height": 2300}, device_scale_factor=2)
    page.goto(url, wait_until="networkidle", timeout=120000)
    for txt in ["Continue", "Go to"]:
        try:
            page.get_by_role("button", name=txt).click(timeout=3000)
        except Exception:
            pass
    try:
        page.wait_for_selector("text=SuperKart System", timeout=120000)
    except Exception:
        page.screenshot(path=f"{ev}/debug_landing.png")
        raise
    time.sleep(3)
    page.screenshot(path=f"{ev}/ui_home.png")
    pick(page, "Store Size", "Medium")
    pick(page, "Store Location City Type", "Tier 2")
    pick(page, "Store Type", "Supermarket Type2")
    pick(page, "Product Type Category", "Non Perishables")
    page.get_by_role("button", name="Predict", exact=True).click()
    page.wait_for_selector("text=Predicted Product Store Sales Total", timeout=60000)
    time.sleep(2)
    page.screenshot(path=f"{ev}/ui_single.png")
    page.locator('input[type="file"]').set_input_files("deploy/Batch_Data_SuperKart.csv")
    time.sleep(3)
    page.get_by_role("button", name="Predict for Batch").click()
    page.wait_for_selector("text=Predictions completed successfully", timeout=60000)
    time.sleep(4)
    page.screenshot(path=f"{ev}/ui_batch.png")
    print("title:", page.title(), "url:", page.url)
    b.close()
