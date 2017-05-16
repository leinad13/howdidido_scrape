## Read current bookings and store in local json database

## Uses - "loginform" - https://pypi.python.org/pypi/loginform
## Uses - "python-dateutil" - https://pypi.python.org/pypi/python-dateutil
## Uses - "tinydb" - https://pypi.python.org/pypi/tinydb
## Uses - "tinydb-serialization" - https://pypi.python.org/pypi/tinydb-serialization/

import scrapy

from loginform import fill_login_form
from scrapy.http import FormRequest
from dateutil.parser import parse
from datetime import datetime
from tinydb import TinyDB, Query
from tinydb_serialization import Serializer
from tinydb_serialization import SerializationMiddleware

## Global Vars ##
# hour_offset - used to adjust the UTC times used by webpage
hour_offset = 1
# db_path - path to the database for persistence
import os
# cwd - Current Working dir
cwd = os.getcwd()

# Function equivilent of xpath normalize-space
def normalize_whitespace(str):
    import re
    str = str.strip()
    str = re.sub(r'\s+', ' ', str)
    return str

# Custom Serializer to store datetime object in tinydb
class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime

    def encode(self, obj):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')

    def decode(self, s):
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')

## register the custom serializer
serialization = SerializationMiddleware()
serialization.register_serializer(DateTimeSerializer(), 'TinyDateTime')

# Main scrapy class
class BookingSpider(scrapy.Spider):
    name = "bookings_read"

    start_urls = ['http://www.howdidido.com/Booking']

    # Login URL - this page has the login form
    login_url = 'https://www.howdidido.com/Account/Login'

    # Files containing username and password, should be ignored by git
    login_passwordfile = open("password.txt")
    login_userfile = open("username.txt")

    # Login User
    login_user = login_userfile.read().strip()
    # Login Password - retreived from the password.txt file
    login_password = login_passwordfile.read().strip()

    def start_requests(self):
        # Send request to login page
        yield scrapy.Request(self.login_url, self.parse_login)

    def parse_login(self, response):
        # Got login page - fill the form...
        data, url, method = fill_login_form(
                                response.url, response.body,
                                self.login_user, self.login_password
                                )
        # ...Send a request with the login data
        return FormRequest(url, formdata=dict(data), method=method, callback=self.start_crawl, dont_filter=True)

    def start_crawl(self, response):
        # Logged in, start crawling protected pages
        for url in self.start_urls:
            yield scrapy.Request(url)

    def parse(self, response):
        # Authentication worked - we are at bookings main page
        for booking in response.xpath('//div[@class="col-lg-4 col-md-6 col-sm-12 col-xs-12"]'):
            booking_link_element = booking.css('div > div > div > div > a')
            booking_link = booking_link_element.css('a::attr(href)').extract_first()

            # Pass link to booking page to next scrape
            yield scrapy.Request(response.urljoin(booking_link),callback=self.parse_booking)

    def parse_booking(self, response):
        # Should be on booking page now...
        # First do some db setup stuff - we need a unique id / name for the competition
        main_title = response.xpath('//span[@class="sub-title"]/text()').extract()
        main_title = main_title[0].replace("/","_")
        db_path = cwd + '\\' + main_title + '.json'
        db_table = datetime.now().strftime('%Y_%m_%dT%H_%M_%S')

        # Database object...
        db = TinyDB(db_path, storage=serialization, default_table=db_table)

        print("DB Path : " + db_path)
        print("DB Table : " + db_table)

        slot_element = response.xpath('//div[@class="slot"]')

        for slot in slot_element:
            timeslots = slot.xpath('.//div[contains(@class, "timeslot")]')

            for timeslot in timeslots:
                data_slotno = timeslot.xpath('./@data-slotno')
                data_time = timeslot.xpath('./@data-time')
                datetimeobj = parse(data_time.extract_first())
                data_bookingname = timeslot.xpath('./@data-bookingname')

                print("data_slotno : " + data_slotno.extract()[0] + "\n")
                print("data_time : " + data_time.extract()[0]+ "\n")
                print("datetimeobj : " + datetimeobj.strftime('%Y_%m_%dT%H_%M_%S') + "\n")
                print("data_bookingname : " + data_bookingname.extract()[0] + "\n")

                ## Insert into database (well json file...)
                db.insert({
                    'bookingtime': datetimeobj,
                    'player_no': data_slotno.extract()[0],
                    'player_name': data_bookingname.extract()[0]
                })
