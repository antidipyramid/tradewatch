from django.db import models


class Senator(models.Model):
    PARTY_CHOICES = [("D", "Democratic"), ("R", "Republican"), ("I", "Independent")]

    last_name = models.CharField(max_length=64)
    first_name = models.CharField(max_length=64)
    party = models.CharField(max_length=2, choices=PARTY_CHOICES)
    state = models.CharField(max_length=2)


class Disclosure(models.Model):
    DISCLOSURE_TYPES = [
        ("P", "Periodic Disclosure"),
        ("A", "Annual Report"),
        ("E", "Extension"),
        ("A", "Amendment"),
    ]
    date = models.DateField()
    senator = models.ForeignKey(Senator, on_delete=models.CASCADE)
    url = models.URLField(max_length=512)
    title = models.CharField(max_length=256)
    related = models.ManyToManyField(
        "self", help_text="Useful to relate amendments to the original disclosure"
    )
    type = models.CharField(max_length=2, choices=DISCLOSURE_TYPES)


class Asset(models.Model):
    name = models.CharField(max_length=64)
    ticker = models.CharField(max_length=8, null=True, blank=True)


class Transaction(models.Model):
    OWNER_CHOICES = [("S", "Self"), ("SP", "Spouse"), ("J", "Joint")]
    ASSET_TYPE_CHOICES = [("S", "Stock")]
    TRANSACTION_TYPE_CHOICES = []
    AMOUNT_CHOICES = []

    date = models.DateField()
    owner = models.CharField(max_length=2, choices=OWNER_CHOICES)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

    senator = models.ForeignKey(Senator, on_delete=models.CASCADE)
    disclosure = models.ForeignKey(Disclosure, on_delete=models.CASCADE)

    type = models.CharField(max_length=2, choices=TRANSACTION_TYPE_CHOICES)
    asset_type = models.CharField(max_length=2, choices=ASSET_TYPE_CHOICES)

    comment = models.TextField()
