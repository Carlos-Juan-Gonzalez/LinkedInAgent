from dotenv import load_dotenv
import os
from playwright.async_api import async_playwright

load_dotenv()

async def create_post(post: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state="src\\scrapping\\session.json")
        page = await context.new_page()
        try:
            await page.goto(os.getenv("LINKEDIN_MAIN_PAGE") or "")
        except Exception:
            print("Failed trying to reach the main page")
        await page.locator("#navigation-create-post-Crear-una-publicaci-n").click()
        await page.fill(".ql-editor", post)
        await page.locator('button[id*="ember"]:has-text("Publicar")').click()
