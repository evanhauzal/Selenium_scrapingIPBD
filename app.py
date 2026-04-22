from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

print("Mulai scraping...")

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get("https://www.wired.com")
time.sleep(5)

# Scroll
for i in range(5):
    driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);"
    )
    time.sleep(3)
    print(f"Scroll ke-{i+1}")

articles = driver.find_elements(By.TAG_NAME, "a")

data = []
visited = set()

for article in articles:

    title = article.text.strip()
    link = article.get_attribute("href")

    if (
        title and
        link and
        "/story/" in link and
        link not in visited
    ):

        visited.add(link)

        clean_link = link.split("#")[0]

        try:
            driver.execute_script(
                "window.open(arguments[0]);",
                clean_link
            )

            driver.switch_to.window(driver.window_handles[1])

            wait = WebDriverWait(driver, 10)

            author = "Unknown"

            selectors = [
                'a[rel="author"]',
                '[class*="Byline"] a',
                '[class*="byline"] a',
                '[data-testid="Byline"] a',
                'div[class*="byline"]',
                'span[class*="byline"]',
            ]

            for selector in selectors:
                try:
                    element = wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, selector)
                        )
                    )

                    text = element.text.strip()

                    if text:
                        author = text.replace("By ", "")
                        break

                except:
                    continue

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except:
            author = "Unknown"

        data.append({
            "title": title,
            "link": clean_link,
            "author": author
        })

# Convert ke DataFrame
df = pd.DataFrame(data)

if df.empty:
    print("❌ Data kosong!")
else:

    df = df.drop_duplicates(subset=['link'])
    df = df.head(50)

    df.to_json(
        "wired_articles.json",
        orient="records",
        indent=4
    )

    print("✅ Berhasil:", len(df))
    print(df.head())

driver.quit()
print("Selesai!")