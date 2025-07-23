import requests
import json
import csv
import time
import html2text
import re
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re

import time
start_time = time.time()


def get_job_description_naukri(url, headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    try:
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        wait = WebDriverWait(driver, 15)
        # desc_element = wait.until(EC.presence_of_element_located(
        #     (By.CSS_SELECTOR, "section[class^='styles_job-desc-container']"))
        # )
        # jd_text = desc_element.text.strip()

        # ✅ Click "read more" if it exists
        try:
            read_more = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[class^='styles_read-more-link']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", read_more)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", read_more)
            time.sleep(1)
        except Exception as e:
            pass  # "read more" not found — ignore and move on
            # print("ℹ️ 'Read more' not found or click failed:", e) # "read more" not found — ignore and move on

        details = {
            'Role': None,
            'Industry Type': None,
            'Department': None,
            'Employment Type': None,
            'Role Category': None
        }
        # Find all <div> blocks that contain a <label>
        detail_blocks = driver.find_elements(By.XPATH, "//div[label]")

        for block in detail_blocks:
            try:
                label_elem = block.find_element(By.TAG_NAME, "label")
                label = label_elem.text.strip().rstrip(":")  # e.g. 'Role'
                
                # Get the text of the following <span>
                value_elem = block.find_element(By.TAG_NAME, "span")
                value = value_elem.text.strip()

                if label in details:
                    details[label] = value

            except Exception as e:
                continue  # safely skip any malformed block

        # print("Details found:", details)  # Debugging line to see what details were extracted
        
        # ✅ Now get the full JD
        desc_element = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "section[class^='styles_job-desc-container']"))
        )
        jd_text = desc_element.text.strip()


        skill_elements = driver.find_elements(By.CSS_SELECTOR, "div.styles_key-skill__GIPn_ a span")
        skills = [elem.text.strip().lower() for elem in skill_elements if elem.text.strip()]

        return jd_text, sorted(set(skills)), details

    except Exception as e:
        print("❌ Selenium scraping failed:", e)
        return "❌ Job description not found", []

    finally:
        driver.quit()


import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
]

def generate_headers():
    return {
        "appid": "109",
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "clientid": "d3skt0p",
        "content-type": "application/json",
        "gid": "LOCATION,INDUSTRY,EDUCATION,FAREA_ROLE",
        "nkparam": "plzUjb4e3MtcOg7niUtLT4T9N+7dakrxw+/Fl/noUSve7ZboozSCwpNJJdCZN3tk5iAfHZvC2aA06Mx4RT+6yw==",
        "priority": "u=1, i",
        "referer": "https://www.naukri.com/data-engineer-jobs?k=data%20engineer",
        "sec-ch-ua": "'Chromium';v='137', 'Google Chrome';v='137', 'Not.A/Brand';v='24'",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "'Windows'",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "systemid": "Naukri",
        "User-Agent": random.choice(USER_AGENTS)
        # "Cookie": ""  # Optional: leave out if not needed
    }


import requests
import time

def get_search_results(params, max_retries=3):
    for attempt in range(max_retries):
        headers = generate_headers()
        try:
            res = requests.get(
                "https://www.naukri.com/jobapi/v3/search",
                headers=headers,
                params=params,
                timeout=20
            )
            if res.status_code == 200:
                return res.json()
            elif res.status_code in [403, 406]:
                print(f"⛔ Blocked with status {res.status_code}. Retrying in 60s...")
                time.sleep(60)
            else:
                print(f"⚠️ Unexpected status {res.status_code}. Retrying in 10s...")
                time.sleep(10)

        except Exception as e:
            print("❌ Network error:", e)
            time.sleep(15)

    return None  # All retries failed



url = "https://www.naukri.com/jobapi/v3/search"
# params = {
#     "noOfResults": 20,
#     "urlType": "search_by_keyword",
#     "searchType": "adv",
#     "keyword": "data engineer",
#     "pageNo": 1,
#     "k": "data engineer",
#     "seoKey": "data-engineer-jobs",
#     "src": "jobsearchDesk",
#     "latLong": ""
# }

# HEADERS_SEARCH = {
#     "appid": "109",
#     "accept":"application/json",                # This might be required (based on Naukri’s site)
#     "accept-language":"en-US,en;q=0.9",
#     "clientid":"d3skt0p",
#     "content-type":"application/json",
#     "gid":"LOCATION,INDUSTRY,EDUCATION,FAREA_ROLE",
#     "nkparam":"plzUjb4e3MtcOg7niUtLT4T9N+7dakrxw+/Fl/noUSve7ZboozSCwpNJJdCZN3tk5iAfHZvC2aA06Mx4RT+6yw==",
#     "priority":"u=1, i",
#     "referer":"https://www.naukri.com/data-engineer-jobs?k=data%20engineer",
#     "sec-ch-ua":"'Chromium';v='136', 'Google Chrome';v='136', 'Not.A/Brand';v='99'",
#     "sec-ch-ua-mobile":"?0",
#     "sec-ch-ua-platform":"'Windows'",
#     "sec-fetch-dest":"empty",
#     "sec-fetch-mode":"cors",
#     "sec-fetch-site":"same-origin",
#     "systemid": "Naukri",             # Often required
#     "Accept": "application/json",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
#     "Cookie":"test=naukri.com; _t_us=68382344; _t_s=direct; _t_r=1030%2F%2F; persona=default; _t_ds=2662f7521748509508-362662f752-02662f752; J=0; _ga=GA1.1.1045481938.1748509509; ak_bmsc=1BEA87FE1F0AC768A495623C5B8B1C80~000000000000000000000000000000~YAAQHtksMTh1IceWAQAAushJGxtVfXW5Y2TGl6nKoOp4ArLpIbqVDbKVpXijonJ9rHmeFuRpE0U8h0AI+uWZL5IirPCnsCu2fY7hOyVBbu4U3e61FO2/PAKZuUZZshuf1ShEmY7NsInzefhFX3nUY152pSnb5vJQOV1DSKMHDHrjQB0iWeA+7aUL5yWcb+YViH2FpzeQMMYhJx0LyROcLRQsR4ljqD0okKSJXo9y+JCbHaw/JohHvHMCAniL6vSUgd3hRb3BbBJpJFlbXUutvebftKUrZJNJ2HwFJpAlQEFPeivOij7sRPFQPTnXbohdbi+45rwuJUYePh+t8MOxut6dsmnNKc6YTlLi37qIUOMMslRhnyL79nLYZcvSlsCm0miPKjDR2ZXRaw6PlrTwX1YqgaYW24HXhlhyh0XbrdQlSmMvKYvvKgSzlVhrb/cjw6LZ5E5ZiKgzkP/JE6HgNOBfvHPQPT5embR67yRqZTXsut2awc8=; _gcl_au=1.1.390230163.1748509510; _ga_T749QGK6MQ=GS2.1.s1748509509^$o1^$g1^$t1748509522^$j47^$l0^$h0; __gads=ID=0f0a2d9475746f09:T=1748509524:RT=1748509524:S=ALNI_MbKJM1bWKFlS9aE67am7HcWXeXxzA; __gpi=UID=00001105bddd8d9c:T=1748509524:RT=1748509524:S=ALNI_MbpfCE8MJSEGU5gqeOKm660Jgnbug; __eoi=ID=9ba87395436b8de6:T=1748509524:RT=1748509524:S=AA-AfjY3skrbCxfNqpCzgGq20XQZ; jd=290525915784; bm_sv=F0B6F453931E225F02F2FC29B8ED1521~YAAQ9PY3F2wxzcKWAQAAMcRVGxumno72PRBefpNDT981QtiUf1MNxzXocPVHZzgeYzVcti+3MduHgoWqGigNvmo/I3AW+BjFtR499IZsePXZNGPvbJNqiOxu/jVjyXQgo5JuTFX7YQtr5Gs9pSD3P79cT/YqYoROMIqzEIhekjDerCFGWLGHlRDhtNb4OhXHUgP3rhXfC1+3d3ioWkvqv/1G4/gnGkBKdpFPErxppz+sY62DnukeT9tu74W/1eXPIA==~1; HOWTORT=ul=1748510294874&r=https%3A%2F%2Fwww.naukri.com%2Fdata-engineer-jobs%3Fk%3Ddata%2520engineer&hd=1748510295091; _ga_K2YBNZVRLL=GS2.1.s1748509509^$o1^$g1^$t1748510295^$j60^$l0^$h0"
# }

html_to_text = html2text.HTML2Text()
html_to_text.ignore_links = True
html_to_text.ignore_images = True
html_to_text.body_width = 0

file_path = "naukri_skills_jobs_safe.csv"

def clean_jd_text(raw):
    raw = raw.strip()
    raw = re.sub(r'\n{2,}', '\n', raw)
    return "".join(line.strip() for line in raw.splitlines())

def get_placeholder(placeholders, key):
    for item in placeholders:
        if item.get("type") == key:
            return item.get("label", "N/A")
    return "N/A"

# --- Persistent job ID cache ---
def load_scraped_ids(filepath="scraped_job_ids2.txt"):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_scraped_id(job_id, filepath="scraped_job_ids2.txt"):
    with open(filepath, "a") as f:
        f.write(job_id + "\n")

# scraped_job_ids = set()




# == Software & Engineering
# Software Engineer, Backend Developer, Full Stack Developer, Frontend Developer,  DevOps Engineer, Site Reliability Engineer (SRE), Embedded Systems Engineer, Mobile App Developer

# == Data & AI
# Data Scientist, Data Analyst, Data Engineer, Machine Learning Engineer, NLP Engineer, Business Intelligence (BI) Developer, AI Researcher

# == Cloud & Infrastructure
# Cloud Engineer, AWS Solution Architect, Azure Cloud Engineer, Cloud Security Engineer, System Administrator

# == Testing & QA
# QA Engineer, Automation Test Engineer, Performance Test Engineer

# == Product & Management
# Product Manager, Project Manager, Scrum Master

# == Cybersecurity & Networking
# Cybersecurity Analyst, Network Engineer

# == Analytics & Business
# Business Analyst, Financial Analyst

# --- Skills (limit to 5–10 for safety per run) ---
# skills = [
#     "Data Engineer", "Java Developer"         //DONE
# ]

# skills = [
#     "Full Stack Developer", "Software Engineer", "Backend Developer", "Frontend Developer", "DevOps Engineer", "Site Reliability Engineer", "Embedded Systems Engineer", "Mobile App Developer"        # DONE
#       "Data Scientist", "Data Analyst", "Machine Learning Engineer", "NLP Engineer",  "Business Intelligence (BI) Developer", "AI Researcher",
#       , , "Azure Cloud Engineer", "Cloud Security Engineer", "System Administrator", "QA Engineer", "Automation Test Engineer", "Performance Test Engineer",
#       "Product Manager", "Project Manager", "Scrum Master", "Cybersecurity Analyst", "Network Engineer", "Business Analyst", "Financial Analyst"
# ] //all roles

# skills = [
#     , , "Site Reliability Engineer", ,         # DONE
#        "Business Analyst", "Financial Analyst"
# ]     // roles remaining to scrape

skills = []     # to be executed


def safe_scrape():
    count = 0
    scraped_job_ids = load_scraped_ids()
    write_header = not os.path.exists(file_path)  # Write header only if file doesn't exist
    with open("naukri_skills_jobs_safe2.csv", mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["Role", "Title", "Company", "Industry Type", "Department", "Employment Type","Role Category", "Experience", "Salary", "Location", "JD URL", "Full JD", "Job ID", "Required Skills", "Short Skills"])

        for skill in skills:
            wrd = skill.lower().replace(" ", "-")
            referer=f"https://www.naukri.com/{wrd}-jobs?k={skill}"

            # HEADERS_SEARCH["referer"]=referer
            HEADERS_SEARCH = generate_headers()
            HEADERS_SEARCH["referer"] = referer

            print(f"\n🔍 Scraping for skill: {skill}")
            for page in range(1, 51):  # 50 pages per skill
                print(f"  📄 Page {page}...")
                params = {
                    "noOfResults": 20,
                    "keyword": skill,
                    "pageNo": page,
                    "urlType": "search_by_keyword",
                    "searchType": "adv",
                    "k": skill,
                    "seoKey": skill.lower().replace(" ", "-") + "-jobs",
                    "src": "jobsearchDesk",
                    "latLong": ""
                }

                try:
                    # res = requests.get("https://www.naukri.com/jobapi/v3/search", headers=HEADERS_SEARCH, params=params)
                    # if res.status_code != 200:
                    #     print(f"    ❌ Search API error: {res.status_code}")
                    #     time.sleep(60)
                    #     continue
                    # jobs = res.json().get("jobDetails", [])

                    data = get_search_results(params)
                    if not data:
                        print("❌ Failed to get results after retries.")
                        continue
                    jobs = data.get("jobDetails", [])

                    
                    if not jobs or not isinstance(jobs, list) or len(jobs) == 0:
                        print(f"    ⛔ No more jobs found on page {page}. Stopping skill.")
                        break  # exit page loop

                    for job in jobs:
                        job_id = job.get("jobId", "")
                        if job_id in scraped_job_ids:
                            continue  # skip duplicate

                        scraped_job_ids.add(job_id)
                        save_scraped_id(job_id)
                        title = job.get("title", "")
                        company = job.get("companyName", "")

                        placeholders = job.get("placeholders", [])

                        experience = get_placeholder(placeholders, "experience")
                        salary = get_placeholder(placeholders, "salary")
                        location = get_placeholder(placeholders, "location")

                        # jd_url = job.get("jdURL", "")
                        jd_url = f"https://www.naukri.com{job.get('jdURL')}"


                        cjd, extracted_skills, details = get_job_description_naukri(jd_url, headless=False)
                        req_skills = extracted_skills

                        req_skills_short = job.get('tagsAndSkills')
                        print(f"    ✅ {title} at {company}")

                        writer.writerow([skill, title, company, details['Industry Type'], details['Department'], details['Employment Type'], details['Role Category'], experience, salary, location, jd_url, cjd, job_id, req_skills, req_skills_short])
                        count = count + 1
                        time.sleep(random.uniform(1.5, 2.5))
                except Exception as e:
                    print(f"    ❌ Error: {e}")
                    time.sleep(60)
                time.sleep(random.uniform(5, 10))  # Cooldown after page   

                if page % 10 == 0:
                    print("Long cooldown after 10 pages...")
                    time.sleep(random.uniform(30, 60)) 

            print("  ⏸️ Cooldown before next skill...")
            time.sleep(random.uniform(15, 25))

        print("\n✅ Jobs scraped:", count)
        print("\n✅ Scraping completed safely! Data saved to 'naukri_skills_jobs_safe2.csv'")

        end_time = time.time()
        total_time = end_time - start_time

        # print(f"\n✅ Scraping complete. Total time taken: {total_time:.2f} seconds.")

        mins, secs = divmod(total_time, 60)
        print(f"\n✅ Done in {int(mins)} minutes and {int(secs)} seconds.")

# --- Run ---
if __name__ == "__main__":
    safe_scrape()