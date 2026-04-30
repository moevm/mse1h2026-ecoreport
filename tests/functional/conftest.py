import pytest
import os

from dotenv import dotenv_values


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox", "--disable-setuid-sandbox",
                "--disable-features=StrictSiteIsolation,HttpsUpgrades",
            ]
        )

        yield browser
        
        browser.close()


@pytest.fixture
def page(browser, base_url):
    context = browser.new_context(
        base_url=base_url,
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True
    )
    
    page = context.new_page()
    
    yield page
    
    context.close()


@pytest.fixture
def base_url():
    # port = "8080"
    # if os.path.exists("src/env/app.env"):
    #     env_vars = dotenv_values("src/env/app.env")
    #     port = env_vars.get("APP_PORT", "8080")
    
    return os.getenv("APP_URL", f"http://localhost:8081")
