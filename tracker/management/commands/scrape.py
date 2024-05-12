from datetime import datetime
from dataclasses import dataclass

from django.core.management.base import BaseCommand, CommandError

from scrapers.senate import SenateTransactionScraper

from tracker.models import Disclosure, Senator, Asset, Transaction


class Command(BaseCommand):
    help = "Scrapes and imports transactions"

    def already_scraped(self, disclosure):
        date_obj = datetime.strptime(disclosure.date, "%m/%d/%Y")
        try:
            Disclosure.objects.get(
                date=date_obj, senator__last_name__icontains=disclosure.last_name
            )
            return True
        except Disclosure.DoesNotExist:
            return False

        return False

    def resolve_senator(self, first_name, last_name, state):
        try:
            senator = Senator.objects.get(state=state, last_name=last_name)
        except Senator.DoesNotExist:
            senator = Senator.objects.create(
                first_name=first_name, last_name=last_name, state=state
            )

        return senator

    def import_disclosure(self, disclosure):
        senator = self.resolve_senator(
            disclosure.first_name, disclosure.last_name, disclosure.state
        )
        d = Disclosure.objects.create(
            date=disclosure.date,
            senator=senator,
            url=disclosure.url,
            scanned=disclosure.image,
            type=disclosure.disclosure_type,
        )

        for transaction in disclosure.transactions:
            Transaction.objects.create(
                date=transaction.date,
                owner=transaction.owner,
                disclosure=d,
                senator=senator,
                asset_type=transaction.asset_type,
                comment=transaction.comment,
            )

    def handle(self, *args, **options):
        for disclosure in SenateTransactionScraper().scrape():
            print(disclosure)
            breakpoint()
            if not self.already_scraped(disclosure):
                print("NEW DISCLOSURE")
                self.import_disclosure(disclosure)
            else:
                print("Already scraped")
