import json
import re
import time
import urllib

import PySimpleGUI as sg
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def main():
	sg.theme("DarkAmber")

	layout = [
		[sg.Text("Enter URL")],
		[sg.Input(key="url", size=(50, 1))],
		[sg.Text("Enter Save Path"), sg.InputText(), sg.FolderBrowse(key="save_path")],
		[sg.Button("Download", key="download"),sg.Text("", key="status", size=(50, 1))],
	]

	window = sg.Window("Box Downloader", layout)

	while True:
		event, values = window.read()
		if event in (sg.WIN_CLOSED, "Exit"):
			break
		if event == "download":
			window["status"].update("Downloading...")
			if values["url"] == "":
				window["status"].update("URL cannot be empty")
				continue
			if values["save_path"] == "":
				window["status"].update("Save Path cannot be empty")
				continue
			if values["url"].startswith("https://app.box.com/s/") == False:
				window["status"].update("Invalid URL")
				continue
			url = values["url"]
			pdf_url = get_url(url)
			file_download(pdf_url, values["save_path"] + "/download.pdf")
	window.close()


def file_download(url, save_path):
	try:
		with urllib.request.urlopen(url) as box_file, open(save_path, 'wb') as local_file:
			local_file.write(box_file.read())
	except urllib.error.URLError as e:
		print(e)


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