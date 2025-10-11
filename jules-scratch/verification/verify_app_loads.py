from playwright.sync_api import Page, expect

def test_app_loads(page: Page):
    """
    This test verifies that the app loads correctly after the refactoring.
    """
    # 1. Arrange: Go to the app's homepage.
    page.goto("http://localhost:19006")

    # 2. Assert: Check for the presence of the dashboard title.
    expect(page.get_by_text("Dashboard")).to_be_visible()

    # 3. Screenshot: Capture the final result for visual verification.
    page.screenshot(path="jules-scratch/verification/verification.png")