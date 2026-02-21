import asyncio
from playwright.async_api import async_playwright

async def build_schedule_site():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("Connecting to ShiftLab...")
        await page.goto("https://verge.myshiftlab.app/timeClock")

        # Login
        await page.fill('input[id="_Form__Field_:r2:"]', "m.dorsey@vergemobile.com")
        await page.fill('input[id="_Form__Field_:r3:"]', "Chuke89!")
        await page.click('button[type="submit"]')

        # Wait for data
        print("Waiting for shifts to load...")
        await page.wait_for_selector("text=Upcoming Shifts", timeout=20000)
        await page.wait_for_timeout(5000) # Give it 5 seconds to finish loading

        # Grab all the text on the page to find the shifts
        # This is a 'catch-all' way to make sure we don't miss the times
        elements = await page.query_selector_all("div[role='button']")
        
        shift_rows_html = ""
        for el in elements:
            text = await el.inner_text()
            if "PA Warminster" in text:
                # This cleans up the text into a nice format
                clean_text = text.replace('\n', ' | ')
                shift_rows_html += f"""
                <tr style="background-color:#FFEBCD; color:#00008B;">
                    <td style="padding:15px; border:solid 2px #000;"><b>Work Shift</b></td>
                    <td style="padding:15px; border:solid 2px #000;">{clean_text}</td>
                    <td style="padding:15px; border:solid 2px #000;">Practice Right Mindfulness today.</td>
                </tr>
                """

        # Create the HTML file
        full_html = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Mark's Schedule</title>
          </head>
          <body style="background-color: #1a1a1a; color: white; font-family: sans-serif; padding: 20px;">
            <h2 style="text-align:center;">Daily Mindfulness & Work</h2>
            <table style="width:100%; max-width:800px; margin:auto; background-color:#F8F8FF; color:black; border-collapse:collapse;">
              <tr style="background-color:#8B0000; color:#FFEBCD;">
                <th style="padding:15px; border:solid 2px #000;">Category</th>
                <th style="padding:15px; border:solid 2px #000;">Details</th>
                <th style="padding:15px; border:solid 2px #000;">Mindful Intent</th>
              </tr>
              {shift_rows_html if shift_rows_html else "<tr><td colspan='3'>No shifts found. Check login or site status.</td></tr>"}
            </table>
          </body>
        </html>
        """

        with open("index.html", "w") as f:
            f.write(full_html)
            
        await browser.close()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(build_schedule_site())
