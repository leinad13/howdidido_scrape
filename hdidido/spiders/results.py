import scrapy

from loginform import fill_login_form
from scrapy.http import FormRequest

class ResultSpider(scrapy.Spider):
    name = "results_read"

    start_urls = ['http://www.howdidido.com/My/Results']

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
        # Authentication worked - we are at main page
        # Selector for each competition row
        #main-content > div > div > table > tbody > tr
        # remove the .extract_first and uncomment the for loop to return to scraping all competitions
        competitions = response.css('#main-content > div > div > table > tbody > tr')

        outerlink = competitions.css('a:nth-child(1)')
        hyperlink = response.urljoin(outerlink.css('a::attr(href)').extract_first())
        yield scrapy.Request(hyperlink, callback=self.parseresult)

        '''
        for competition in competitions :
            # Link to specific competition selector
            # a:nth-child(1)
            outerlink = competition.css('a:nth-child(1)')
            hyperlink = response.urljoin(outerlink.css('a::attr(href)').extract_first())
            title = outerlink.xpath('text()').extract_first()
            yield scrapy.Request(hyperlink, callback=self.parseresult)
        '''

    def parseresult(self, response):
        headingobj = response.css('#main-content > div > div > h1 > span')
        title = headingobj.xpath('//*[@id="main-content"]/div/div/h1/span/text()').extract_first()
        date = response.xpath('//*[@id="main-content"]/div/div/h1/span/span/text()').extract_first()

        ''' Uncomment to write out the compeition html
        outfile = open('competitions/'+title,'w')
        outfile.write(response.body)
        '''
        person_rows = response.css('.result > tbody:nth-child(2) > tr')
        for person_row in person_rows:
            person_position = person_row.xpath('tr > td.text-center.hidden-xs::text').extract()
            person = person_row.css('a::text').extract()
            person_score = person_row.css('tr > td.text-right.text-nowrap::text').extract()
            person_handicap = person_row.css('tr > td:nth-child(4)::text').extract()

            yield {
                'title': title,
                'date': date,
                'position': person_position,
                'person': person,
                'person_handicap': person_handicap,
                'person_score': person_score
            }
