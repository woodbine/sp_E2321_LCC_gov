# -*- coding: utf-8 -*-
import os
import re
import requests
import scraperwiki
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup
from dateutil.parser import parse
from dateutil.rrule import rrule, MONTHLY
from datetime import time
import time
from datetime import datetime
from datetime import datetime

# Set up variables
entity_id = "E2321_LCC_gov"
st_date = datetime(int(2014),int(1),int(1))
end_date = datetime(int(2015),int(6),int(1))
start_urls = ['http://www3.lancashire.gov.uk/transparency/spending/SupplierPayments.asp?Period=%s&Version=1' % dt.strftime('%m%Y') for dt in rrule(MONTHLY, dtstart=st_date, until=end_date)]
data = {'strAction': 'exportCSV', 'strOutputFields':'service_lable', 'strOutputFields':'service_code',
        'strOutputFields':'organisational_unit', 'strOutputFields':'expenditure_category',
        'strOutputFields':'expenditure_code', 'strOutputFields': 'payment_date', 'strOutputFields':'transaction_number',
        'strOutputFields':'amount', 'strOutputFields':'supplier_name'}


#url = 'http://www3.lancashire.gov.uk/transparency/spending/SupplierPayments.asp?Period=062015&Version=1'
errors = 0
# Set up functions
def validateFilename(filename):
    filenameregex = '^[a-zA-Z0-9]+_[a-zA-Z0-9]+_[a-zA-Z0-9]+_[0-9][0-9][0-9][0-9]_[0-9][0-9]$'
    dateregex = '[0-9][0-9][0-9][0-9]_[0-9][0-9]'
    validName = (re.search(filenameregex, filename) != None)
    found = re.search(dateregex, filename)
    if not found:
        return False
    date = found.group(0)
    year, month = int(date[:4]), int(date[5:7])
    now = datetime.now()
    validYear = (2000 <= year <= now.year)
    validMonth = (1 <= month <= 12)
    if all([validName, validYear, validMonth]):
        return True
def validateURL(url):
    try:
        r = requests.post(url, data =data, allow_redirects=True, timeout=20)
        count = 1
        while r.status_code == 500 and count < 4:
            print ("Attempt {0} - Status code: {1}. Retrying.".format(count, r.status_code))
            count += 1
            r = requests.post(url, data =data, allow_redirects=True, timeout=20)
        sourceFilename = r.headers.get('Content-Disposition')
        if sourceFilename:
            ext = os.path.splitext(sourceFilename)[1].replace('"', '').replace(';', '').replace(' ', '')
        elif r.headers['Content-Type'] == 'text/csv':
             ext = '.csv'
        else:
            ext = os.path.splitext(url)[1]
        validURL = r.status_code == 200
        validFiletype = ext in ['.csv', '.xls', '.xlsx', '.CSV']
        return validURL, validFiletype
    except:
        raise
def convert_mth_strings ( mth_string ):

    month_numbers = {'JAN': '01', 'FEB': '02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06', 'JUL':'07', 'AUG':'08', 'SEP':'09','OCT':'10','NOV':'11','DEC':'12' }
    #loop through the months in our dictionary
    for k, v in month_numbers.items():
#then replace the word with the number

        mth_string = mth_string.replace(k, v)
    return mth_string
# pull down the content from the webpage


for url in start_urls:
    html = requests.post(url, data =data,  allow_redirects=True)
    csvYr = url.split('&')[0].split('=')[-1][-4:]
    csvMth = url.split('&')[0].split('=')[-1][:2]
    filename = entity_id + "_" + csvYr + "_" + csvMth
    todays_date = str(datetime.now())
    file_url = url
    validFilename = validateFilename(filename)
    validURL, validFiletype = validateURL(file_url)
    if not validFilename:
        print filename, "*Error: Invalid filename*"
        print file_url
        errors += 1
        continue
    if not validURL:
        print filename, "*Error: Invalid URL*"
        print file_url
        errors += 1
        continue
    if not validFiletype:
        print filename, "*Error: Invalid filetype*"
        print file_url
        errors += 1
        continue
    scraperwiki.sqlite.save(unique_keys=['l'], data={"l": file_url, "f": filename, "d": todays_date })
    print filename

if errors > 0:
     raise Exception("%d errors occurred during scrape." % errors)
