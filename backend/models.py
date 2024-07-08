from django.db import models
from django.utils.translation import gettext_lazy as _


class Platform(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Supplier(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    title = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    scrape_frequency = models.IntegerField(default=3600)
    last_scrape_at = models.DateTimeField('last scrape at', null=True)

    def __str__(self):
        return self.title


class Giveaway(models.Model):
    class Type(models.TextChoices):
        GAME = "GAME", _("Game")
        DEMO = "DEMO", _("Demo")
        DLC = "DLC", _("DLC")
        LOOT = "LOOT", _("Loot")
        ALPHA = "ALPHA", _("Alpha")
        BETA = "BETA", _("Beta")
        MEMBERSHIP = "MEMBERSHIP", _("Membership")
        OTHER = "OTHER", _("Other")
        # TODO: add credits?

    class Status(models.TextChoices):
        CREATED = "CREATED", _("Created")
        QUEUED = "QUEUED", _("Queued")
        PUBLISHED = "PUBLISHED", _("Published")
        CANCELED = "CANCELED", _("Canceled")
        EXPIRED = "EXPIRED", _("Expired")

    platforms = models.ManyToManyField(Platform, blank=True)
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        default=Type.OTHER,
    )
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    url = models.TextField(blank=True)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True)
    msrp = models.FloatField(null=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.CREATED,
    )
    created_at = models.DateTimeField(
        'created at', auto_now_add=True, blank=True)
    updated_at = models.DateTimeField('updated at', auto_now=True, blank=True)
    expiration_date = models.DateTimeField('expiration date', null=True)
    publish_to_socials = models.BooleanField(default=True)
    show_source = models.BooleanField(default=False)
    post_id = models.TextField(blank=True)
    post_title = models.TextField(blank=True)
    post_url = models.TextField(blank=True)
    post_image = models.TextField(blank=True)
    steam_grid_db_image = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        platforms = []
        if self.pk:
            for platform in self.platforms.all():
                platforms.append(str(platform))
        platforms_text = ' / '.join(platforms) if platforms else 'Other'
        type_text = self.type if self.type else 'Other'
        return f'[{platforms_text}] ({type_text}) {self.title}\n{self.description}'
