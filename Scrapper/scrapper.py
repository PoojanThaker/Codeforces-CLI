from Scrapper.utils import Problem
import json
from bs4 import BeautifulSoup, NavigableString
import csv
from Scrapper.constants import *
import requests


class Scrapper:
    """
    Abstract scrapper class
    """
    def __init__(self, scraped_problems_file):
        self.scraped_problems_file = scraped_problems_file

    def fetch_urls(self, batch_mode):
        raise NotImplementedError("The method is not implemented")

    def url_to_problem(self, url):
        raise NotImplementedError("The method is not implemented")

    def sync_problems(self):
        scrapped_problems = {}
        with open(self.scraped_problems_file, 'rt') as file:
            reader = csv.reader(file)
            for row in reader:
                scrapped_problems.update({str(row[0]): True})
        urls = self.fetch_urls(scrapped_problems)
        for url in urls:
            problem = self.url_to_problem(url)
            # TODO varshil db.put_problem(problem)


class CodeforcesScrapper(Scrapper):

    def __init__(self):
        super().__init__(CODEFORCES_SCRAPED_PROBLEMS_FILE)

    def fetch_urls(self, scrapped_problems):
        urls = []
        page = requests.get(CODEFORCES_PROBLEMSET_URL)
        soup = BeautifulSoup(page.content, 'html5lib')
        pagination_div = soup.find('div', {'class': 'pagination'})
        total_pages = int(pagination_div.findAll('li')[-2].find('span')['pageindex'])
        for page in range(total_pages):
            page = requests.get(CODEFORCES_PROBLEMSET_URL+'/page/'+str(page+1))
            soup = BeautifulSoup(page.content, 'html5lib')
            table = soup.find('table', {'class': 'problems'})
            rows = table.find_all('tr')
            for row in rows[1:]:
                problem_id_div = row.find('td', {'class': 'id'})
                problem_id = problem_id_div.find('a').text.replace(' ', '').replace('\n', '')
                if problem_id not in scrapped_problems:
                    problem_url = problem_id_div.find('a')['href'].replace(' ', '').replace('\n', '')
                    urls.append(CODEFORCES_URL + problem_url)
                    print(problem_id_div.find('a').text.replace(' ', '').replace('\n', ''))
                    print(problem_id_div.find('a')['href'].replace(' ', '').replace('\n', ''))
        return urls

    def get_problem_id(self, url):
        return '_'.join(url.split('/')[-2:])

    def _process_div(self, divs):
        processed_div = {}
        for num, div in enumerate(divs):
            if isinstance(div, NavigableString):
                continue
            key = ''.join(['line', str(num)])
            processed_div.update({key: str(div.text)})
        images = divs.findAll("img")
        if images:
            image_url = [image['src'] for image in images]
            processed_div.update({'images': image_url})
        return processed_div

    def url_to_problem(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html5lib')
        statement = soup.find("div", {"class": "problem-statement"})
        problem_dict = {}
        key_list = ['header', 'statement', 'input', 'output', 'examples', 'note']
        for i, div in enumerate(statement):
            problem_dict.update({key_list[i]: self._process_div(div)})
        problem_json = json.dumps(problem_dict, indent=4)
        return Problem(self.get_problem_id(url), url, CODEFORCES, None, problem_json)
