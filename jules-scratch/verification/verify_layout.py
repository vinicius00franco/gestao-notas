from playwright.sync_api import sync_playwright, expect

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:8081/--/web/App")

    # Open the drawer
    page.click('[data-testid="drawer-button"]')

    # Click the "Classificar Notas" link
    page.click('text="Classificar Notas"')

    # Wait for the screen to load
    expect(page.locator('text="Não Classificado"')).to_be_visible()

    page.screenshot(path="jules-scratch/verification/verification.png")
    browser.close()