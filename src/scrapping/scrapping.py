from dotenv import load_dotenv
import os
import asyncio
from playwright.async_api import async_playwright
from datetime import date

load_dotenv()

async def get_impressions():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state="src\\scrapping\\session.json")
        page = await context.new_page()

        try:
            await page.goto(os.getenv("LINKEDIN_FEED_PAGE") or "")
        except Exception:
            print("Failed trying to reach the feed")
        
        for i in range(50):
            await page.keyboard.press("PageDown")
            await asyncio.sleep(0.1)

        posts = (await page.query_selector_all(".break-words.tvm-parent-container"))
        impressions = (await page.query_selector_all(".ca-entry-point__num-views"))
    
        data = []

        for i, (post_el, imp_el) in enumerate(zip(posts, impressions)):
            post_content = await post_el.inner_text()
            impression_text = await imp_el.inner_text()

            try:
                num_impressions = int(''.join(filter(str.isdigit, impression_text)))
            except ValueError:
                print(f"No se pudieron extraer impresiones del post {i}")
                continue
            
      
            data.append({
                "post": post_content[:15].strip(),
                "impressions": [
                    {
                        "num_impressions": num_impressions,
                        "date": date.today().isoformat()
                    }
                ]
            })

        await browser.close()
        return data
