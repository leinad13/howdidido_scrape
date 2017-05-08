## Howdidido test scrape script
## Login uses : https://github.com/scrapy/loginform
## To install the required module loginform : "pip install loginform"
## Some help from : http://stackoverflow.com/questions/29809524/using-loginform-with-scrapy

## password is stored in file - "password.txt", so it can be excluded from the git repo.

## WIP - http://www.howdidido.com/Booking


import scrapy
from loginform import fill_login_form
from scrapy.http import FormRequest

class LoginSpider(scrapy.Spider):
    name = 'how'

    # Main URL - script will start proper scraping from here after login
    start_urls = ['http://www.howdidido.com/']

    # Login URL - this page has the login form
    login_url = 'https://www.howdidido.com/Account/Login'
    # Files which contains password, username is ignored by git
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
        # Authentication worked - we are at main page
        # Get handicap - uses css selector to get then regex to get the value between the two rounded brackets
        handicap = response.css('#timeline > div > div.welcome.m-b-0 > span.pull-right > a').re('\(([^)]+)\)')

        yield {
            'handicap': handicap
        }
