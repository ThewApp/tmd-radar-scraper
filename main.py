import logging
import os
from time import sleep
from urllib.parse import urlparse
import sqlite3
import hashlib
import requests
from bs4 import BeautifulSoup

ENDPOINTS = ["https://weather.tmd.go.th/bma_nck.php",
             "https://weather.tmd.go.th/bma_nkm.php"]

DATA_DIR = "data"
IMAGE_DIR = os.path.join(DATA_DIR, "images")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", filename=os.path.join(DATA_DIR, "main.log"))
logger = logging.getLogger(__name__)

con = sqlite3.connect(IMAGE_DIR + ".db")

cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS images (
    image_id INTEGER PRIMARY KEY,
    endpoint TEXT,
	image_src TEXT NOT NULL,
	image_hash TEXT NOT NULL,
    image_datetime INT NOT NULL,
    image_file TEXT
)""")
con.commit()
cur.close()

while True:
    logger.info("Scraping")
    for endpoint in ENDPOINTS:
        try:
            page = requests.get(endpoint, timeout=10)
        except requests.Timeout as err:
            logger.warning("requests.Timeout %s", err)
            continue
        except requests.exceptions.RequestException:
            logger.warning("requests.exceptions.RequestException %s", err)
            continue
        if (page.status_code == 200):
            imgTag = BeautifulSoup(page.content, 'html.parser').img
            if imgTag:
                src = imgTag["src"]
                try:
                    img = requests.get(src, timeout=5).content
                    digest = hashlib.blake2b(img).hexdigest()
                    cur = con.cursor()
                    cur.execute(
                        "SELECT image_id FROM images WHERE image_hash = ?", (digest,))
                    if not cur.fetchone():
                        cur.execute(
                            """
                            INSERT INTO images (endpoint, image_src, image_hash, image_datetime)
                            VALUES (?,?,?, strftime('%s','now'))
                            """, (endpoint, src, digest))
                        file_id = cur.execute(
                            "SELECT image_id FROM images WHERE image_hash = ?", (digest,)).fetchone()[0]
                        (filename, ext) = os.path.splitext(
                            os.path.basename(urlparse(src).path))
                        filename = f"{filename}_{file_id:09}{ext}"
                        filepath = os.path.join(IMAGE_DIR, filename)
                        cur.execute(
                            "UPDATE images SET image_file = ? WHERE image_id = ?", (filename, file_id))
                        with open(filepath, 'wb') as fd:
                            fd.write(img)
                        logger.info("Retrieved %s as %s", src, filename)
                    else:
                        logger.debug(
                            "Image with hash %s already existed", digest)
                    con.commit()
                    cur.close()
                except requests.Timeout as err:
                    logger.warning("requests.Timeout %s", err)
                except sqlite3.Error as err:
                    logger.error("sqlite3: %s", err)
                except Exception as err:
                    logger.warning(f"Could not retrieve {src}: {err}")

    sleep(60)
