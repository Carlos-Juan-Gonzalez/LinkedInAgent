# guardar_sesion.py
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        page = await context.new_page()
        await page.goto("https://www.linkedin.com/login")

        print("log in manually then press enter on the console when you are done.")
        input(">> Waiting for log in...")

        # Guarda cookies y storage
        await context.storage_state(path="session.json")
        await browser.close()

asyncio.run(main())
