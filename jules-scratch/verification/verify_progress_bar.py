from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        page.goto("http://localhost:8081/", timeout=120000)

        # Click on the "Upload" button in the tab bar
        page.get_by_text("Upload").click()

        # Wait for the upload screen to load
        expect(page.get_by_text("Selecione o arquivo da Nota Fiscal")).to_be_visible(timeout=120000)

        # Simulate file selection by setting the state directly
        page.evaluate("() => { window.setFile({ uri: 'fake-uri', name: 'test.pdf', type: 'application/pdf' }); }")

        # Fill in the CNPJ
        page.get_by_placeholder("CNPJ").fill("12345678901234")

        # Click the process button
        page.get_by_role("button", name="Processar Nota").click()

        try:
            # Wait for the job status screen to load
            expect(page.get_by_text("Job:")).to_be_visible(timeout=120000)
            page.screenshot(path="jules-scratch/verification/verification.png")
        except Exception as e:
            print(f"An error occurred during navigation: {e}")
            page.screenshot(path="jules-scratch/verification/navigation_error.png")

    except Exception as e:
        print(f"An error occurred: {e}")
        page.screenshot(path="jules-scratch/verification/error.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)