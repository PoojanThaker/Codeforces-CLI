from Scrapper.utils import Problem
import json
from bs4 import BeautifulSoup, NavigableString
from Scrapper.constants import CODEFORCES
import requests


class Scrapper:
    """
    Abstract scrapper class
    """

    def fetch_urls(self, batch_mode):
        raise NotImplementedError("The method not implemented")

    def url_to_problem(self, url):
        raise NotImplementedError("The method not implemented")

    def sync_problems(self, batch_mode=True):
        batches = self.fetch_urls(batch_mode)
        for batch in batches:
            for url in batch:
                self.url_to_problem(url)


class CodeforcesScrapper(Scrapper):
    def fetch_urls(self, batch_mode):
        # TODO by spj
        pass

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
