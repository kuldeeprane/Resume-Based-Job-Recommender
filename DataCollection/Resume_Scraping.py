import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
import time
import csv
from collections import deque
import re

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeScraper:
    def __init__(self, base_url, csv_filename="resumes.csv"):
        self.base_url = base_url
        self.visited_pages = set()
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        self.csv_filename = csv_filename


    def fetch_page(self, url):
        try:
            logger.info(f"Fetching URL: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def extract_pagination_links(self, soup):
        links = set()
        for a in soup.select("a.pager"):
            href = a.get("href")
            if href:
                full = urljoin(self.base_url, href)
                links.add(full)
        return links

    def extract_resume_blocks(self, soup):
        return soup.find_all("div", class_="snippetPadding")

    def extract_resume_data(self, resume_url):
        soup = self.fetch_page(resume_url)
        if not soup:
            return None

        try:
            title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "N/A"
            location_tag = soup.find("a", class_="colorLocation")
            location = location_tag.get_text(strip=True) if location_tag else "N/A"
            date_tag = soup.find("span", class_="colorDate")
            posted_date = date_tag.get_text(strip=True) if date_tag else "N/A"
            resume_div = soup.find("div", class_="normalText") or soup.find("div", id="resumetext")
            resume_text = resume_div.get_text("\n", strip=True) if resume_div else "N/A"

            return {
                "title": title,
                "location": location,
                "posted_date": posted_date,
                "link": resume_url,
                "resume": resume_text
            }

        except Exception as e:
            logger.warning(f"Error parsing resume at {resume_url}: {e}")
            return None

    def scrape_all_resumes(self, start_url):
        to_visit = deque([start_url])

        while to_visit:
            current_url = to_visit.popleft()
            if current_url in self.visited_pages:
                continue
            self.visited_pages.add(current_url)

            soup = self.fetch_page(current_url)
            if not soup:
                continue

            resume_blocks = self.extract_resume_blocks(soup)
            for block in resume_blocks:
                a_tag = block.find("a")
                if not a_tag or not a_tag.get("href"):
                    continue
                resume_url = urljoin(self.base_url, a_tag["href"])
                resume_data = self.extract_resume_data(resume_url)
                if resume_data:
                    print("=" * 80)
                    print(f"Title       : {resume_data['title']}")
                    print(f"Location    : {resume_data['location']}")
                    print(f"Posted Date : {resume_data['posted_date']}")
                    print(f"Link        : {resume_data['link']}")
                    print("Resume Text :\n" + resume_data['resume'].encode('utf-8', errors='replace').decode('utf-8'))
                    print("=" * 80)

                    # Write to CSV
                    with open(self.csv_filename, mode='a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            resume_data['title'],
                            resume_data['location'],
                            resume_data['posted_date'],
                            resume_data['link'],
                            resume_data['resume']
                        ])

                    time.sleep(1)  # Be polite

            # Add new pagination links
            new_pages = self.extract_pagination_links(soup)
            to_visit.extend(sorted(new_pages - self.visited_pages, key=self.page_sort_key))

    def page_sort_key(self, url):
        match = re.search(r'resumes\?p=(\d+)', url)
        return int(match.group(1)) if match else float('inf')


# Run the scraper
if __name__ == "__main__":
    BASE_URL = "https://www.postjobfree.com"
    csv_filename = "resumes.csv"

    # Initialize CSV only once
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Location", "Posted Date", "Link", "Resume Text"])

    # Create a single scraper instance
    scraper = ResumeScraper(BASE_URL, csv_filename)

    locs = [
        "/resumes?q=title%3A%28{i}%29&l=kolkata&radius=500",
        "/resumes?q=title%3A%28{i}%29&l=Bengaluru&radius=500",
        "/resumes?q=title%3A%28{i}%29&l=Pune&radius=500",
        "/resumes?q=title%3A%28{i}%29&l=Noida&radius=500",
    ]

    job_roles = [
        # Software & Engineering
        "Software Engineer", "Backend Developer", "Full Stack Developer", "Frontend Developer",
        "DevOps Engineer", "Site Reliability Engineer (SRE)", "Embedded Systems Engineer", "Mobile App Developer",

        # Data & AI
        "Data Scientist", "Data Analyst", "Data Engineer", "Machine Learning Engineer",
        "NLP Engineer", "Business Intelligence (BI) Developer", "AI Researcher",

        # Cloud & Infrastructure
        "Cloud Engineer", "AWS Solution Architect", "Azure Cloud Engineer",
        "Cloud Security Engineer", "System Administrator",

        # Testing & QA
        "QA Engineer", "Automation Test Engineer", "Performance Test Engineer",

        # Product & Management
        "Product Manager", "Project Manager", "Scrum Master",

        # Cybersecurity & Networking
        "Cybersecurity Analyst", "Network Engineer",

        # Analytics & Business
        "Business Analyst", "Financial Analyst"
    ]

    for job in job_roles:
        for loc in locs:
            start_url = f"{BASE_URL}/{loc.format(i=job)}"
            scraper.scrape_all_resumes(start_url)
