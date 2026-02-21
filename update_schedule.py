import asyncio
from playwright.async_api import async_playwright

async def build_schedule_site():
    async with async_playwright() as p:
        # 1. Launch Browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # 2. Login
        print("Logging into ShiftLab...")
        await page.goto("https://verge.myshiftlab.app/timeClock", wait_until="networkidle")
        await page.fill('input[id="_Form__Field_:r2:"]', "m.dorsey@vergemobile.com")
        await page.fill('input[id="_Form__Field_:r3:"]', "Chuke89!")
        await page.click('button[type="submit"]')

        # 3. Wait for the data to actually appear
        print("Waiting for shifts...")
        await page.wait_for_selector('[data-testid="shift-time"]', timeout=30000)
        await page.wait_for_timeout(3000) # Final breath for rendering

        # 4. Target the specific containers
        # We look for the parent "card" that holds the time, date, and location
        # On ShiftLab, these are usually grouped in buttons or divs
        shift_cards = await page.query_selector_all("div[role='button']")
        
        shift_rows_html = ""
        found_count = 0

        for card in shift_cards:
            # Check if this card actually contains a shift time
            time_element = await card.query_selector('[data-testid="shift-time"]')
            if time_element:
                found_count += 1
                full_text = await card.inner_text()
                # Clean up the text for the table
                clean_text = " ".join(full_text.split())
                
                shift_rows_html += f"""
                <tr style="background-color:#FFEBCD; color:#00008B;">
                    <td style="padding:15px; border:solid 2px #000;"><b>Scheduled Shift</b></td>
                    <td style="padding:15px; border:solid 2px #000;">{clean_text}</td>
                    <td style="padding:15px; border:solid 2px #000;">Remember: Work is an opportunity for practice.</td>
                </tr>
                """

        # 5. Build the Final HTML
        full_html = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Mark's Schedule</title>
            <style>
              body {{ background-color: #1a1a1a; color: white; font-family: sans-serif; padding: 20px; }}
              table {{ width:100%; max-width:800px; margin:auto; background-color:#F8F8FF; color:black; border-collapse:collapse; }}
              tr.header {{ background-color:#8B0000; color:#FFEBCD; }}
              td, th {{ padding:15px; border:solid 2px #000; }}
            </style>
          </head>
          <body>
            <h2 style="text-align:center;">Mark Timothy Dorsey: Work & Mindfulness</h2>
            <table>
              <tr class="header">
                <th>Category</th>
                <th>Shift Details</th>
                <th>Mindful Intention</th>
              </tr>
              {shift_rows_html if shift_rows_html else "<tr><td colspan='3'>No shifts found in the dashboard.</td></tr>"}
            </table>
          </body>
        </html>
        """

        with open("index.html", "w") as f:
            f.write(full_html)
            
        await browser.close()
        print(f"Success! Found and formatted {found_count} shifts.")

if __name__ == "__main__":
    asyncio.run(build_schedule_site())
