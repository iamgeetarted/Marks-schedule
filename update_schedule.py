import asyncio
from playwright.async_api import async_playwright

async def build_schedule_site():
    async with async_playwright() as p:
        # 1. Launch Browser
        browser = await p.chromium.launch(headless=True)
        # We use a standard laptop screen size
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()

        print("Step 1: Connecting to ShiftLab...")
        await page.goto("https://verge.myshiftlab.app/timeClock", wait_until="networkidle")

        # 2. Login
        print("Step 2: Logging in...")
        await page.fill('input[id="_Form__Field_:r2:"]', "m.dorsey@vergemobile.com")
        await page.fill('input[id="_Form__Field_:r3:"]', "Chuke89!")
        await page.click('button[type="submit"]')

        # 3. Wait for the specific Test ID you found
        print("Step 3: Waiting for shift data to appear...")
        try:
            # We wait up to 30 seconds for your specific data-testid
            await page.wait_for_selector('[data-testid="shift-time"]', timeout=30000)
            print("Target found! Extracting data...")
        except Exception as e:
            print(f"Error: Timed out waiting for shift-time. Saving debug screenshot.")
            await page.screenshot(path="debug_error.png")
            return

        # 4. Extract every shift time found
        # This targets the exact ID you provided
        times = await page.get_by_test_id("shift-time").all_text_contents()
        
        # We also want the dates/locations. 
        # Since they are in the same 'card', we grab the parent containers.
        shift_cards = await page.query_selector_all("div[role='button']")
        
        shift_rows_html = ""
        for card in shift_cards:
            inner_text = await card.inner_text()
            if "PA Warminster" in inner_text or "9:" in inner_text:
                clean_text = " ".join(inner_text.split())
                shift_rows_html += f"""
                <tr style="background-color:#FFEBCD; color:#00008B;">
                    <td style="padding:15px; border:solid 2px #000;"><b>Work Shift</b></td>
                    <td style="padding:15px; border:solid 2px #000;">{clean_text}</td>
                    <td style="padding:15px; border:solid 2px #000;">Mindfulness: Watch the breath during busy moments.</td>
                </tr>
                """

        # 5. Generate Final HTML
        full_html = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Mark's Live Schedule</title>
          </head>
          <body style="background-color: #1a1a1a; color: white; font-family: sans-serif; padding: 20px;">
            <h2 style="text-align:center; color:#FFEBCD;">Mark Timothy Dorsey: Schedule & Practice</h2>
            <table style="width:100%; max-width:800px; margin:auto; background-color:#F8F8FF; color:black; border-collapse:collapse; border: 3px solid #8B0000;">
              <tr style="background-color:#8B0000; color:#FFEBCD;">
                <th style="padding:15px; border:solid 2px #000;">Type</th>
                <th style="padding:15px; border:solid 2px #000;">Details</th>
                <th style="padding:15px; border:solid 2px #000;">Dharma Intention</th>
              </tr>
              {shift_rows_html if shift_rows_html else "<tr><td colspan='3'>Dashboard loaded, but no shifts found for this week.</td></tr>"}
            </table>
          </body>
        </html>
        """

        with open("index.html", "w") as f:
            f.write(full_html)
            
        await browser.close()
        print(f"Successfully updated with {len(times)} shift times.")

if __name__ == "__main__":
    asyncio.run(build_schedule_site())
