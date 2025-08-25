import logging
import time
import json
from datetime import datetime
from seleniumwire import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

PATH = "..\\data\\data.json"

# ========== Helper ==========
def safe_get_text(element, by, value, default="N/A"):
    try:
        return element.find_element(by, value).text.strip()
    except:
        return default

def safe_get_attr(element, by, value, attr="href", default="N/A"):
    try:
        return element.find_element(by, value).get_attribute(attr).strip()
    except:
        return default
# ========== Main Actions ==========
def smart_scroll_panel(driver, panel):
    try:
        target = panel.find_element(By.ID, "detail-bewerbung-url")
        driver.execute_script("arguments[0].scrollIntoView(true);", target)
        return True
    except:
        pass

    try:
        scrollable = panel.find_element(By.CSS_SELECTOR, "div.modal-body")
        actions = ActionChains(driver)
        actions.move_to_element(scrollable).click().perform()
        for _ in range(5):
            actions.send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(0.5)
        return True
    except Exception as e:
        print("Scroll fail:", e)
        return False

def accept_cookies():
    while True:
        ans = input("👉Have you clicked 'Alle Cookies akzeptieren' and solved the captcha on the first job yet? (y/n): \n").strip().lower()
        if ans == "y":
            logging.warning("✅ The cookie banner has been dismissed (user confirmed).")
            return True
        if ans == "n":
            logging.warning("❌ The user has not clicked the cookie banner.")
            return False
        
def extract_job_detail(driver, wait: WebDriverWait):
    panel = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "jb-job-detail")))
    smart_scroll_panel(driver, panel)

    return {
        "Profession": safe_get_text(panel, By.ID, "detail-kopfbereich-titel"),
        "Company Name": safe_get_text(panel, By.ID, "detail-kopfbereich-firma"),
        "Location": safe_get_text(panel, By.ID, "detail-kopfbereich-arbeitsort"),
        "Start Date": safe_get_text(panel, By.ID, "detail-kopfbereich-eintrittsdatum-mit-datum"),
        "Telephone": safe_get_text(panel, By.ID, "detail-bewerbung-telefon-Telefon"),
        "Email": safe_get_text(panel, By.ID, "detail-bewerbung-mail"),
        "Job Description": safe_get_text(panel, By.ID, "detail-beschreibung-beschreibung"),
        "Ref.-Nr.": safe_get_text(panel, By.ID, "detail-footer-referenznummer"),
        "Application Link": safe_get_attr(panel, By.ID, "detail-bewerbung-url")
    }

def extract_jobs_from_ul(page_index, driver, wait: WebDriverWait, ul_id: str, start_index=0):
    results = []
    try:
        job_list_ul = wait.until(
            EC.presence_of_element_located((By.ID, ul_id))
        )
    except:
        logging.warning(f"❌ Not found {ul_id}")
        return results

    job_items = job_list_ul.find_elements(By.TAG_NAME, "li")
    logging.warning(f".📄 Crawling data from page: {page_index}")

    for idx in range(start_index, len(job_items)):
        # re-find để tránh lỗi stale element
        job_items = job_list_ul.find_elements(By.TAG_NAME, "li")
        job = job_items[idx]

        driver.execute_script("arguments[0].scrollIntoView(true);", job)
        time.sleep(0.5)
        job.click()

        job_info = extract_job_detail(driver, wait)
        results.append(job_info)
        save_json(results)
        logging.warning(f". . ✅ {idx} / {len(job_items)} jobs crawled.")
        close_job_detail(driver)

    return results

def close_job_detail(driver):
    """Đóng panel job detail nếu có nút Close."""
    try:
        close_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "detailansicht-close")))
        close_btn.click()
    except:
        pass

def click_load_more(driver, wait):
    """Bấm nút 'Weitere Ergebnisse' để load thêm jobs."""
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 300);")
        time.sleep(1)
        load_more = wait.until(
            EC.presence_of_element_located((By.ID, "ergebnisliste-ladeweitere-button"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", load_more)
        time.sleep(2)
        logging.warning(". ✅ Load more jobs")
        return True
    except Exception as e:
        logging.error(f". ❌ Can not load more jobs: {e}")
        return False

def save_json(new_data):
    try:
        data = json.load(open(PATH, encoding="utf-8"))
    except:
        data = []
    if not isinstance(data, list): data = [data]
    data += new_data if isinstance(new_data, list) else [new_data]
    json.dump(data, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=4)

# ========== Main ==========
def main():
    options = {"request_storage_base_dir": "./requests"}
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/137.0.0.0 Safari/537.36")

    url = "https://www.arbeitsagentur.de/jobsuche/suche?angebotsart=4&ausbildungsart=0&arbeitszeit=vz&branche=22;1;2;9;3;5;7;10;11;16;12;21;26;15;17;19;20;8;23;29&veroeffentlichtseit=7&sort=veroeffdatum"

    with webdriver.Chrome(seleniumwire_options=options, options=chrome_options) as driver:
        wait = WebDriverWait(driver, 10)
        driver.get(url)

        if not accept_cookies():
            return []

        all_jobs, page_index = [], 1
        while True:
            ul_id = f"ergebnisliste-liste-{page_index}"
            all_jobs.extend(extract_jobs_from_ul(page_index, driver, wait, ul_id))
            if not click_load_more(driver, wait):
                break
            page_index += 1

        logging.warning(f"\n🎯 Done !!! Getted {len(all_jobs)} jobs")
        


if __name__ == "__main__":
    main()
