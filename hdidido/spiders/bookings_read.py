## Read current bookings

import scrapy

from loginform import fill_login_form
from scrapy.http import FormRequest

# Function equivilent of xpath normalize-space
def normalize_whitespace(str):
    import re
    str = str.strip()
    str = re.sub(r'\s+', ' ', str)
    return str

class BookingSpider(scrapy.Spider):
    name = "bookings_read"

    start_urls = ['http://www.howdidido.com/Booking']

    # Login URL - this page has the login form
    login_url = 'https://www.howdidido.com/Account/Login'
    # File which contains password, is ignored by git
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
            booking_title = normalize_whitespace(booking_link_element.css('a::text').extract_first())
            booking_link = booking_link_element.css('a::attr(href)').extract_first()

            yield {
                'booking_link': booking_link,
                'booking_title': booking_title
            }
