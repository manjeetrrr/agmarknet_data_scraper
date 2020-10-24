# @author: laterknight
# note - script doesn't check for the files already downloaded as it is time consuming 
# because the final tally is around 7 lakh files and it will get stuck in infinite loop as there are some days where there is no file to download. 
# It only checks for internet availability and then resumes while internet is back again,
# the resume function is not actually fool proof 
# as it tends to forget 1-2 file where the exception first occured it resumes after 1-2 files

import os
import time
import urllib3 as ul 
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime, timedelta, date
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

start_date = date(2015, 1, 1) #date format == year, month, date
end_date = date(2015, 1, 3)
path = '/home/laterknight/Downloads/Agmarknet_Price_And_Arrival_Report.xls'
counter = 0

driver = webdriver.Chrome('/home/laterknight/Downloads/chromedriver') #change if path differs
link = 'http://agmarknet.gov.in/'
http = ul.PoolManager()
page =http.request('GET',link)
soup = BeautifulSoup(page.data)

hh = webdriver.ChromeOptions() # driver = webdriver.Chrome(chrome_options=hh)
hh.add_argument("--start-maximized")
driver.get(link) #opening the link in the driver .

commodity_element = driver.find_element_by_id('ddlCommodity')
commodity_select = Select(commodity_element)
commodity_values = [ '%s' % o.get_attribute('value') for o in commodity_select.options[1:]]

def select_commodity_option(value):
	arrival_price_element = driver.find_element_by_id('ddlArrivalPrice')
	arrival_price_select = Select(arrival_price_element)
	arrival_price_select.select_by_value('2')

	commodity_element = driver.find_element_by_id('ddlCommodity')
	commodity_select = Select(commodity_element)
	commodity_select.select_by_value(value)

print(commodity_values)

for value in commodity_values:
	d = start_date
	condition = True
	print("downloading data for commodity: {}".format(value))
	#selecting arrival_price and commodity
	select_commodity_option(value)
	
	print("commodites completed %s" %counter) #Progress Tracker
	remaining = len(commodity_values) - counter
	print("commodites remaining %s" %remaining)

	while condition:
		try:
			input_date = datetime.strftime(d, "%m-%d-%y") #variables for date and input
			year = datetime.strftime(d, "%y")
			month = datetime.strftime(d, "%m")
			day = datetime.strftime(d, "%d")
			
			inputElement = driver.find_element_by_id("txtDate")#submitting forms
			inputElement.clear()
			inputElement.send_keys(input_date)
			inputElement.send_keys(Keys.ENTER)

			time.sleep(3) #adjust time.sleep if the internet connection of the computer speed is too slow.
			driver.find_element_by_id('cphBody_ButtonExcel').click() #Downloading Excel File

			time.sleep(3) #renaming
			if os.path.exists(path):
				os.rename(path, '/home/laterknight/Downloads/%s_%s_%s_%s.xls'%(value, year, month, day))

			if d == end_date:
				condition=False
		
			d += timedelta(days=1) #Advancing the day
			print(input_date)
		
		except NoSuchElementException:
			no_internet_connection = True
			while no_internet_connection:
				try:
					driver.get(link)
					xx = driver.find_element_by_class_name('error-code').text
					if xx == 'ERR_INTERNET_DISCONNECTED':
						print(xx)
						print('retrying')
						time.sleep(10)
				except NoSuchElementException:
					no_internet_connection = False

			select_commodity_option(value)

	counter += 1