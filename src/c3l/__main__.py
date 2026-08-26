#!/usr/bin/env python3

import webbrowser
from sys import exit, stderr
from urllib.parse import urlencode
from argparse import ArgumentParser, ArgumentTypeError, RawTextHelpFormatter
import phonenumbers as pn
import re
import os


def eprint(*args, **kwargs):
	print("\x1b[31m[-]\x1b[0m", *args, file=stderr, **kwargs)

def wprint(*args, **kwargs):
	print("\x1b[33m[!]\x1b[0m", *args, file=stderr, **kwargs)

def oprint(*args, **kwargs):
	print("\x1b[32m[+]\x1b[0m", *args, **kwargs)


def phone_validation(ps: str) -> pn.PhoneNumber:
	p = None
	try:
		if not ps.startswith("+"):
			ps = "+" + ps
			wprint(f"Incomplete phone number, assumed '{ps}'")
		p = pn.parse(ps, None)
	except pn.phonenumberutil.NumberParseException:
		raise ArgumentTypeError("Missing or invalid default region")
	if not pn.is_possible_number(p):
		raise ArgumentTypeError("Impossible phone format")
	if not pn.is_valid_number(p):
		raise ArgumentTypeError("Invalid phone format")
	return p

def username_validation(username: str) -> str:
	if not username:
		raise ArgumentTypeError(f"Invalid username '{username}'")
	return username.strip()

def email_validation(email: str) -> str:
	if not email or not re.match(r"(^\s*[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\s*$)", email):
		raise ArgumentTypeError(f"Invalid email '{email}'")
	return email.strip()

def test_file(test: str) -> str:
	if not test or not os.path.isfile(f"tests/{test}.html"):
		raise ArgumentTypeError(f"Invalid test script '{test}'")
	return f"tests/{test}.html"

def sites_validation(sites: str) -> list[str]:
	if not sites or sites == "-":
		return []
	sites_list = [site.strip() for site in sites.split(",")]
	for site in sites_list:
		if not re.match(r"^[a-z0-9.-]+$", site):
			raise ArgumentTypeError(f"Invalid site '{site}'")
	return sites_list


SITES = [
	"linkedin.com",
	"instagram.com",
	"facebook.com",
	"reddit.com",
	"twitter.com",
	"github.com",
	"quora.com"
]
AUTH_WAIT_TIME = 600 # Time to wait for user to authenticate (in seconds)
WAIT_TIME = 15 # Time to wait for elements to load (in seconds)
GOOGLE_WAIT_TIME = AUTH_WAIT_TIME # Time to wait for user to authenticate on Google (in seconds)


if __name__ == "__main__":
	parser = ArgumentParser(epilog="Default sites to inspect:"+ ', '.join(f'{"\n  " if (not (i % 4)) else ""}{SITES[i]}' for i in range(len(SITES))), formatter_class=RawTextHelpFormatter)
	
	command_group = parser.add_mutually_exclusive_group(required=True)
	command_group.add_argument('phone', type=phone_validation, nargs='?') #, help='Phone number to search for (in international format, e.g. +1234567890). You can also pass a username or email with the -u or -e flag respectively')
	command_group.add_argument('-u', '--username', type=username_validation, nargs='+', help='search for a username instead')
	# command_group.add_argument('-e', '--email', type=email_validation, nargs='+', help='search for an email instead')
	parser.add_argument('-m', '--manual', action="store_true", help="do not automate searching, only open in default browser (do not require Selenium to be installed)")
	parser.add_argument('-f', '--full', action="store_true", help="do not stop at the first found result")
	parser.add_argument('--test', type=test_file, help="test to run")
	parser.add_argument('--sites', type=sites_validation, help="comma-separated list of sites to inspect. '-' or '' (empty) to inspect all sites")
	parser.add_argument('-a', '--anonymous', action="store_true", help="do not use any account to search (results may be limited and less accurate)")
	parser.add_argument('-d', '--debug', action="store_true", help="debug")
	args = parser.parse_args()


	def iprint(*_args, **kwargs):
		if args.debug:
			print("\x1b[34m[*]\x1b[0m", *_args, **kwargs)

	iprint("Search parameters:", args)

	if args.phone is not None:
		# National
		phone_format_national = pn.format_number(args.phone, pn.PhoneNumberFormat.NATIONAL) #[1:]
		phone_list = [
			phone_format_national,
			phone_format_national.replace(' ', '.'),
			phone_format_national.replace(' ', ''),

			# Dashes and brackets popular in some regions
			# https://en.wikipedia.org/wiki/National_conventions_for_writing_telephone_numbers
			phone_format_national.replace('-', ''),
			phone_format_national.replace('(', '').replace(')', ''),
			phone_format_national.replace('-', '').replace('(', '').replace(')', ''),
			phone_format_national.replace('-', '').replace(' ', ''),
		]

		# International
		phone_format_international = pn.format_number(args.phone, pn.PhoneNumberFormat.INTERNATIONAL)[1:]
		# phone_format = re.sub(r"^(\[ \.\(\)-\]\+)", r"(\1)?( ?\(0\))?", phone_format_international.replace(' ', '[ .()-]+'))
		# exit(1)

		phone_list += [
			phone_format_international,
			phone_format_international.replace(' ', '.'),
			phone_format_international.replace(' ', ''),

			# Dashes and brackets popular in some regions
			# https://en.wikipedia.org/wiki/National_conventions_for_writing_telephone_numbers
			phone_format_international.replace('-', ''),
			phone_format_international.replace('(', '').replace(')', ''),
			phone_format_international.replace('-', '').replace('(', '').replace(')', ''),
			phone_format_international.replace('-', '').replace(' ', ''),

			phone_format_international.replace(' ', ' (0)', 1),
		]

		# print(pn.phonenumberutil.number_type(args.phone))
		# exit(0)
		number_type = pn.phonenumberutil.number_type(args.phone)
		if number_type == pn.PhoneNumberType.MOBILE:
			oprint("Mobile number")
		elif number_type == pn.PhoneNumberType.FIXED_LINE_OR_MOBILE:
			oprint("Mobile OR fixed-line number")
		else:
			wprint("Not a mobile number:", pn.PhoneNumberType.to_string(number_type),
				"\nThis phone number isn't associated with a mobile device, so it might be less likely to be found on social media profiles or associated with a physical person.\n"
			"You can pass the '--sites -' argument to search on all sites, which may increase the chances of finding it.")
		
		# iprint("Searching for phone numbers:", phone_list)

	else:
		phone_list = args.username

	# Remove eventual duplicates
	phone_list = list(set(phone_list))
	iprint("Searching for "+ ("phone numbers" if args.phone else "usernames") +":", phone_list)
	# exit(0)

	if args.sites is not None:
		SITES = args.sites

	params = {
		# "cx": "a2a04e3ac38de4635",
		"q": '"'+ '" OR "'.join(phone_list) +'"'+ (' site:'+ ' OR site:'.join(SITES) if SITES else ''),
		# "as_sitesearch": ' '.join(SITES)
		# "udm": 2 # For Google Images, add 'udm=2'
	}

	iprint("Search parameters:", params)

	if args.manual:
		webbrowser.open("https://www.google.com/search?"+urlencode(params))

	else:
		from selenium import webdriver
		from selenium.webdriver.common.by import By
		from selenium.webdriver.support.ui import WebDriverWait
		from selenium.webdriver.support import expected_conditions as EC
		# from selenium.webdriver.common.keys import Keys
		from selenium.webdriver.common.action_chains import ActionChains
		from time import sleep
		from io import BytesIO
		import requests
		from PIL import Image
		import pytesseract
		from dotenv import dotenv_values
		from phonenumbers import geocoder
		import shutil


		browser = None
		try:
			if shutil.which("tesseract") is None:
				raise RuntimeError("tesseract-ocr is required.\nInstall it with:\nsudo apt install tesseract-ocr")

			iprint("Anonymous:", args.anonymous)

			config = dotenv_values(".env")

			browser = webdriver.Chrome()
			# pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract" # Change this if tesseract is not in PATH
			search_url = ("file://"+os.path.abspath(args.test)+"?") if args.test else ("https://www.google.com/search?"+urlencode(params))
			country_name = geocoder.country_name_for_number(args.phone, "en").replace(" ", "").lower() if args.phone else ""

			def phone_number_test(text: str, phone_list: list[str], href: str, full: bool):
				if any(phone in text for phone in phone_list):
					oprint("Phone number found:", href)
					if not full:
						if input('Do you want to continue searching? ')[0].lower() != 'y':
							exit(0)
						args.full = True

			# Check images
			image_hrefs = []
			if True:
				# params["udm"] = 2 # For Google Images, add 'udm=2'
				browser.get(search_url+"&udm=2")
				if not args.test:
					WebDriverWait(browser, GOOGLE_WAIT_TIME).until(
						EC.presence_of_element_located((By.ID, "W0wltc"))
					)
					browser.find_element(By.ID, "W0wltc").click()
				
				WebDriverWait(browser, WAIT_TIME).until(
					EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img.YQ4gaf"))
				)
				result = browser.find_elements(By.CSS_SELECTOR, "img.YQ4gaf")
				for thumbnail in result:
					thumbnail.click()
					WebDriverWait(browser, WAIT_TIME).until(
						EC.presence_of_element_located((By.CLASS_NAME, "iPVvYb"))
					)
					picture = browser.find_element(By.CLASS_NAME, "iPVvYb")
					picture_url = picture.get_attribute("src") or picture.get_property("src")
					# print(picture_url)
					if picture_url.startswith("file://"):
						img = Image.open(picture_url[7:])
					else:
						response = requests.get(picture_url)
						img = Image.open(BytesIO(response.content))
					img = img.convert("L") # Convert to grayscale (makes it easier for OCR)
					text = pytesseract.image_to_string(img)

					phone_number_test(text, phone_list, picture_url, args.full)
					# webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
					break
 
				results = browser.find_elements(By.CSS_SELECTOR, "a.EZAeBe")
				if results:
					image_hrefs = [(a.text, a.get_attribute("href") or a.get_property("href")) for a in results]

				# TODO: Implement checking on the remote page itself, not only on the image

			# Check text results
			search_url = ("file://"+os.path.abspath(args.test)) if args.test else ("https://www.google.com/search?"+urlencode(params))
			browser.get(search_url)
			# if not args.test:
			# 	WebDriverWait(browser, GOOGLE_WAIT_TIME).until(
			# 		EC.presence_of_element_located((By.ID, "W0wltc"))
			# 	)
			# 	browser.find_element(By.ID, "W0wltc").click()
			
			WebDriverWait(browser, WAIT_TIME).until(#EC.any_of(
				EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.A6K0A")),
				# EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.JPMJ2c"))
			)#)
			results = browser.find_elements(By.CSS_SELECTOR, "div.A6K0A")

			if not results:
				eprint("No result found")

			else:
				filtered_hrefs = []
				linkedin_hrefs = []

				for e in results:
					title = e.find_element(By.CSS_SELECTOR, "span.VuuXrf").text
					a = e.find_element(By.CSS_SELECTOR, "a.zReHs")
					href = a.get_attribute("href") or a.get_property("href")
					desc = e.find_element(By.CSS_SELECTOR, "div.VwiC3b").text
					
					# print(title, href, desc)
					if re.match(r"^https:\/\/[a-z-]+\.linkedin\.com", href):
						linkedin_hrefs.append((title, re.sub(r"^(https:\/\/[a-z-]+\.linkedin\.com\/in\/[a-z0-9-]+)(\/.*)?", r"\1", href), desc, country_name in desc.lower()))

					elif any(phone in desc for phone in phone_list):
						filtered_hrefs.append((title, href, desc, country_name in desc.lower()))

				if linkedin_hrefs:
					found = False
					if not args.anonymous:
						if config.get("LINKEDIN_EMAIL") and config.get("LINKEDIN_PASSWORD"):
							browser.get("https://www.linkedin.com/feed/")
							WebDriverWait(browser, WAIT_TIME).until(#EC.any_of(
								EC.presence_of_element_located((By.CSS_SELECTOR, "button.authwall-join-form__form-toggle--bottom")),
								# EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.JPMJ2c"))
							)#)
							browser.find_element(By.CSS_SELECTOR, "button.authwall-join-form__form-toggle--bottom").click()
							email = browser.find_element(By.ID, "session_key")
							email.send_keys(config["LINKEDIN_EMAIL"])
							password = browser.find_element(By.ID, "session_password")
							password.send_keys(config["LINKEDIN_PASSWORD"])
							browser.find_element(By.CSS_SELECTOR, "button.btn-primary").click()
							WebDriverWait(browser, AUTH_WAIT_TIME).until(EC.url_to_be("https://www.linkedin.com/feed/"))
							# sleep(1)

							for title, href, desc, country in linkedin_hrefs:
								browser.get(href+"/recent-activity/all/")
								WebDriverWait(browser, WAIT_TIME).until(
									EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.hrxlpLvxJUJyXIDfmEZuSJbOiiaKKzE > div > div > span > span"))
								)
								posts = browser.find_elements(By.CLASS_NAME, "jPkojJgPCsFiBeJCGftSYDFoPuUXKHXSIZi")
								
								found = False
								for post in posts:
									# ActionChains(browser).move_to_element(browser.sl.find_element_by_id('my-id')).perform()
									text = post.find_element(By.CSS_SELECTOR, "div.hrxlpLvxJUJyXIDfmEZuSJbOiiaKKzE > div > div > span > span").text
									profile = post.find_element(By.CSS_SELECTOR, "div.mSVGjEKhPKDfUgwRSOEVXpeygjVfBDviMQOg a.npCfLwmDwyRGUjjSegPUogjodwpBUsaGQ")
									profile_href = profile.get_attribute("href") or profile.get_property("href")

									if phone_number_test(text, phone_list, profile_href.split('?', 1)[0], args.full):
										found = True
										break
								if found:
									break
							if not found:
								wprint("Phone number not found on LinkedIn profile(s) recent activity, but it may be present on other pages (e.g. contact info, posts older than recent activity, etc.)")
						else:
							wprint("LinkedIn credentials not specified in .env, skipping LinkedIn deep analysis")

					if not found:
						oprint("LinkedIn profile(s) associated with the phone number:")
						for title, href, desc, country in linkedin_hrefs:
							print(f"  {title:<30} {href}")

				if filtered_hrefs:
					oprint("Phone number found")
					filtered_hrefs = sorted(filtered_hrefs, key=lambda x: x[3], reverse=True) # Sort by country match
					for title, href, desc, country in filtered_hrefs:
						print(f"  {title:<30} {href}")

				elif image_hrefs:
					oprint("Phone number found:")
					# image_hrefs = sorted(image_hrefs, key=lambda x: x[1], reverse=True) # Sort by href
					for title, href in image_hrefs:
						print(f"  {title:<30} {href}")

		except RuntimeError as e:
			print()
			eprint(e)
			if browser:
				browser.quit()

		except KeyboardInterrupt:
			print()
			eprint("Interrupted by user")
			if browser:
				browser.quit()

		# while True:
		# 	sleep(1)
