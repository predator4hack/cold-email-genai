from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import random

def scrape_wellfound():
    with sync_playwright() as p:
        # Launch browser with a persistent context to maintain cookies
        browser = p.chromium.launch(headless=False)  # Set to True once everything works
        
        # Create a context with specific options to avoid detection
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            has_touch=False,
            java_script_enabled=True,
            locale='en-US',
            timezone_id='America/New_York',
        )
        
        # Stealth mode
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        # Open a new page
        page = context.new_page()
        
        # Navigate to the website
        page.goto("https://wellfound.com/jobs/3148571-data-scientist")
        
        # Wait for page to load - using a selector that should appear on the page
        try:
            # Add random wait to appear more human-like
            time.sleep(random.uniform(2, 4))
            
            # If there's a CAPTCHA, we need to deal with it
            if "captcha" in page.content().lower():
                print("CAPTCHA detected! Waiting for manual resolution...")
                # Wait for a main content element to appear
                page.wait_for_selector("main", timeout=60000)  # 60 seconds timeout
            
            # Continue after CAPTCHA is resolved (manually or automatically)
            # Additional wait to ensure page is fully loaded
            page.wait_for_load_state("networkidle")
            
            # Get the page content
            html = page.content()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check if we're still getting limited content
            text_content = soup.get_text()
            if len(text_content) < 100:
                print(f"Warning: Limited content detected. Text length: {len(text_content)}")
                print(f"Content: {text_content}")
            else:
                # Extract job listings
                job_listings = soup.find_all("div", class_="job-listing")  # Adjust selector as needed
                print(f"Found {len(job_listings)} job listings")
                
                # Process job listings
                for job in job_listings[:5]:  # Process first 5 for example
                    title = job.find("h2")
                    company = job.find("div", class_="company-name")  # Adjust selector as needed
                    if title and company:
                        print(f"Job: {title.text.strip()} at {company.text.strip()}")
        
        except Exception as e:
            print(f"Error: {e}")
            # Take a screenshot for debugging
            page.screenshot(path="error_screenshot.png")
        
        finally:
            # Close the browser
            browser.close()

if __name__ == "__main__":
    scrape_wellfound()