import json
import re
import sys
import time

import requests
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def main():
	box_url = input("Enter Box URL: ")
	if box_url == "":
		print("URL cannot be empty")
		sys.exit(1)
	if box_url.startswith("https://app.box.com/s/") == False:
		print("Invalid URL")
		sys.exit(1)
	pdf_url = get_url(box_url)
	data = requests.get(pdf_url, stream=True)
	if data.status_code == 200:
		with open("file.pdf", "wb") as f:
			for chunk in data.iter_content(1024):
				f.write(chunk)
		print("File saved as file.pdf")
		sys.exit(0)
	else:
		print("Error downloading file")
		sys.exit(1)


def get_url(box_url):
	options = webdriver.ChromeOptions()
	options.add_argument("headless")
	options.add_argument("--ignore-certificate-errors")

	d = DesiredCapabilities.CHROME
	d["goog:loggingPrefs"] = {"performance": "ALL"}

	driver = webdriver.Chrome(
		service=ChromeService(ChromeDriverManager().install()),
		options=options,
		desired_capabilities=d,
	)

	driver.get(box_url)

	time.sleep(10)

	for log in driver.get_log("performance"):
		network_log = json.loads(log["message"])
		if network_log["message"]["method"] != "Network.requestWillBeSent":
			continue
		if re.search(r"https://dl2.boxcloud.com/api/.*/files/.*/content\?preview=true&version=.*", network_log["message"]["params"]["request"]["url"]):
			download_url = network_log["message"]["params"]["request"]["url"]

	driver.quit()
	return download_url


if __name__ == "__main__":
	main()