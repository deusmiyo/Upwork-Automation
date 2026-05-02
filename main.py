import setuptools  # Fix for 'distutils' missing in Python 3.12+
import ssl
import urllib.request
import undetected_chromedriver as uc
import undetected_chromedriver.patcher

# Fix for SSL: CERTIFICATE_VERIFY_FAILED
# Because undetected-chromedriver caches `urlopen` internally, we MUST patch its specific reference.
_orig_urlopen = urllib.request.urlopen
def _patched_urlopen(*args, **kwargs):
    if 'context' not in kwargs:
        kwargs['context'] = ssl._create_unverified_context()
    return _orig_urlopen(*args, **kwargs)

undetected_chromedriver.patcher.urlopen = _patched_urlopen

import pandas as pd
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def scrape_upwork_jobs(url):

    # Load existing data to avoid duplicates and continue from where we left off
    existing_links = set()
    try:
        df_existing = pd.read_excel('upwork_jobs.xlsx')
        job_names_list = df_existing['Job Name'].dropna().tolist()
        job_links_list = df_existing['Job Link'].dropna().tolist()
        skills_list = df_existing['Tagged Skill'].dropna().tolist()
        existing_links = set(job_links_list)
        print(f"Loaded {len(job_links_list)} existing jobs from Excel.")
    except Exception:
        job_names_list = []
        job_links_list = []
        skills_list = []
        print("Starting with a fresh Excel file.")

    # Initialize undetected-chromedriver
    options = uc.ChromeOptions()
    # Adding options that may help bypass detections
    options.add_argument("--disable-popup-blocking")
    
    # We do NOT use headless=True because we might need to manually solve Captcha
    driver = uc.Chrome(options=options, version_main=147)
    
    try:
        print(f"Navigating to: {url}")
        driver.get(url)
        
        print("Waiting for search results to load...")
        try:
            # Wait for the main card wrapper
            print("--> If you see a Cloudflare Captcha, please solve it manually in the browser window.")
            print("--> Waiting up to 5 minutes for results to appear...")
            WebDriverWait(driver, 300).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-ev-sublocation="search_results"]'))
            )
        except Exception as e:
            print("Could not find search results. You might have timed out waiting for captcha.")
            return

        # Let the page fully render
        time.sleep(2)

        # Locate all job cards initially to get the count
        job_cards = driver.find_elements(By.CSS_SELECTOR, '[data-ev-sublocation="search_results"]')
        count = len(job_cards)
        print(f"Found {count} job impressions on this page.")

        for i in range(count):
            if i == 0:
                print("Skipping first job card...")
                continue
            try:
                # We re-fetch the cards in the loop to avoid StaleElementReferenceException
                current_cards = driver.find_elements(By.CSS_SELECTOR, '[data-ev-sublocation="search_results"]')
                if i >= len(current_cards):
                    break
                
                card = current_cards[i]
                
                # Scroll to card
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                time.sleep(0.5) # Small pause for visual stability
                
                # Click the card directly
                driver.execute_script("arguments[0].click();", card)

                # Wait for the side panel (slider-view) to appear
                slider_locator = (By.CSS_SELECTOR, '.slider-view.air3-card')
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located(slider_locator))
                slider = driver.find_element(*slider_locator)

                # Extract the Job Name from the h1 inside the slider
                h1_loc = (By.CSS_SELECTOR, '.m-0.h4')
                WebDriverWait(slider, 10).until(EC.visibility_of_element_located(h1_loc))
                job_name = slider.find_element(*h1_loc).text.strip()

                # Extract the Job Link using JavaScript for maximum reliability
                try:
                    job_link = driver.execute_script("""
                        // 1. Try the exact data-test attribute you provided
                        var exactLink = document.querySelector('a[data-test="slider-open-in-new-window UpLink"]');
                        if (exactLink && exactLink.href) return exactLink.href;
                        
                        // 2. Try a partial match on the data-test
                        var partialLink = document.querySelector('a[data-test*="slider-open-in-new-window"]');
                        if (partialLink && partialLink.href) return partialLink.href;
                        
                        // 3. Fallback: Find ANY link containing /jobs/~ inside the slider
                        var slider = document.querySelector('.slider-view.air3-card');
                        if (slider) {
                            var links = slider.querySelectorAll('a[href*="/jobs/~"]');
                            if (links.length > 0) return links[0].href;
                        }
                        
                        return "N/A";
                    """)
                except Exception as e:
                    print(f"    -> JS extraction failed. Error: {e}")
                    job_link = "N/A"

                # SKIP if link is N/A or already exists
                if job_link == "N/A" or job_link in existing_links:
                    reason = "N/A link" if job_link == "N/A" else "Duplicate"
                    print(f"[{i+1}/{count}] Skipping ({reason}): {job_name}")
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    try:
                        WebDriverWait(driver, 5).until(EC.invisibility_of_element_located(slider_locator))
                    except:
                        time.sleep(1) # Fallback sleep if wait fails
                    continue

                print(f"[{i+1}/{count}] Processing job: {job_name}")
                existing_links.add(job_link)

                # Check for the trigger button to show more skills
                job_skills = []
                skills_lists = slider.find_elements(By.CSS_SELECTOR, '.skills-list.mt-3')

                def collect_skills(container, job_skills):
                    for el in container.find_elements(By.CSS_SELECTOR, '.air3-line-clamp.is-clamped'):
                        if el.is_displayed():
                            skill_text = el.text.strip()
                            if skill_text and skill_text not in job_skills:
                                job_skills.append(skill_text)

                if skills_lists:
                    base = skills_lists[0]
                    collect_skills(base, job_skills)

                    trigger_btns = base.find_elements(By.CSS_SELECTOR, '.air3-badge.air3-btn.air3-btn-secondary.badge.air3-popper-trigger')
                    if trigger_btns and trigger_btns[0].is_displayed():
                        try:
                            driver.execute_script("arguments[0].click();", trigger_btns[0])
                            time.sleep(1)
                            skills_lists2 = slider.find_elements(By.CSS_SELECTOR, '.skills-list.justify-content-center')
                            if skills_lists2:
                                collect_skills(skills_lists2[0], job_skills)
                        except:
                            pass

                # This clicks the element even if it is hidden by CSS
                element = driver.find_element(By.CSS_SELECTOR, '.d-none.d-md-flex.air3-slider-prev-btn')
                driver.execute_script("arguments[0].click();", element)

                # Add the job name and link to their lists
                job_names_list.append(job_name)
                job_links_list.append(job_link)
                
                # Add all skills to their list
                for skill in job_skills:
                    skills_list.append(skill)

                print(f"Skills: {len(job_skills)}")
                
                # Save to Excel incrementally (filling columns independently)
                df = pd.DataFrame({
                    "Job Name": pd.Series(job_names_list),
                    "Job Link": pd.Series(job_links_list),
                    "Tagged Skill": pd.Series(skills_list)
                })
                df.to_excel('upwork_jobs.xlsx', index=False)

                # Close the side panel to proceed cleanly to the next one
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                try:
                    WebDriverWait(driver, 5).until(EC.invisibility_of_element_located(slider_locator))
                except:
                    # Proceed even if it doesn't hide properly or wait times out
                    pass

            except Exception as e:
                print(f"Failed to scrape job")
                # Attempt to close slider just in case it's stuck open
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(1)

    finally:
        driver.quit()

    # Final Status
    if job_names_list or skills_list:
        print(f"\nSuccess! Saved {len(job_names_list)} jobs and {len(skills_list)} skills to upwork_jobs.xlsx")
    else:
        print("\nNo data was scraped.")

if __name__ == "__main__":
    # For testing: 
    test_url = "https://www.upwork.com/nx/search/jobs/?q=python"
    scrape_upwork_jobs(test_url)
