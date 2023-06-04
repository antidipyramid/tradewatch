# This tool scrapes the publicly available stock transaction disclosures
# required of all sitting U.S. Senators.

import requests
import pandas as pd
import pdb
import time
from dataclasses import dataclass
from functools import partial
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod


BASE = "https://efdsearch.senate.gov/"
URL = "https://efdsearch.senate.gov/search/home/"
HOME = "https://efdsearch.senate.gov/search/"
SEARCH = "https://efdsearch.senate.gov/search/report/data/"

RESULTS_PER_PAGE = 100
STARTDATE = "06/01/2020 00:00:00"
SLEEPLENGTH = 2


@dataclass
class ScrapedDisclosure:
    url: str
    senator: str
    disclosure_type: str
    date: str
    html: str


class TransactionScraper(ABC):
    @abstractmethod
    def scrape(self):
        pass


class SenateTransactionScraper(TransactionScraper):
    def __init__(self, start_date, end_date=""):
        self.session = requests.Session()
        self.start_date = start_date
        self.end_date = end_date

    def get_csrf(self, response):
        soup = BeautifulSoup(response.text, "lxml")
        return soup.find(
            lambda tag: tag.name == "input" and tag.get("name") == "csrfmiddlewaretoken"
        ).get("value")

    def get_links_to_disclosures(self, token, start):

        # POST the JSON data from the site
        # with csrf token from search site

        results = self.session.post(
            SEARCH,
            data={
                "start": str(start),
                "length": str(start + RESULTS_PER_PAGE),
                "report_types": "[11]",
                "filer_types": "[]",
                "submitted_start_date": self.start_date,
                "submitted_end_date": self.end_date,
                "candidate_state": "",
                "senator_state": "",
                "office_id": "",
                "first_name": "",
                "last_name": "",
                "csrfmiddlewaretoken": token,
            },
            headers={"Referer": HOME},
        )

        return results.json()["data"]

    def scrape_results(self, site=URL):
        # Record keeping begins on 01/01/2012 00:00:00

        landing = self.session.get(site)

        # Send a post request to accept the terms of use
        # with csrf token from landing site

        resp = self.session.post(
            URL,
            data={
                "prohibition_agreement": "1",
                "csrfmiddlewaretoken": self.get_csrf(landing),
            },
            headers={"Referer": URL},
        )

        start = 0
        nextResults = self.get_links_to_disclosures(self.get_csrf(resp), start)
        while nextResults:
            yield from nextResults
            start += RESULTS_PER_PAGE
            nextResults = self.get_links_to_disclosures(self.get_csrf(resp), start)
            time.sleep(SLEEPLENGTH)

    def scrape(self):
        for result in self.scrape_results():
            soup = BeautifulSoup(result[3], "html.parser")
            report_url = soup.a["href"]

            yield ScrapedDisclosure(
                report_url, result[2], soup.a.text, result[4], " "
            )


def main():
    results = SenateTransactionScraper(STARTDATE).scrape()
    for result in results:
        print(result)


if __name__ == "__main__":
    main()
