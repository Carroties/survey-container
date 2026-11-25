from datetime import timedelta

from django.core.validators import URLValidator
from django.db import models
from django.utils import timezone

SURVEY_LIFETIME = timedelta(days=7)


class SurveyQuerySet(models.QuerySet):
    def active(self):
        return self.filter(created_at__gt=timezone.now() - SURVEY_LIFETIME)

    def expired(self):
        return self.filter(created_at__lte=timezone.now() - SURVEY_LIFETIME)


class Survey(models.Model):
    title = models.CharField("Nama survei", max_length=160)
    url = models.URLField(
        "Tautan formulir",
        max_length=500,
        validators=[
            URLValidator(
                schemes=["http", "https"],
                message="Masukkan tautan formulir yang dimulai dengan http:// atau https://.",
            ),
        ],
    )
    sender = models.CharField("Nama pengirim", max_length=100)
    contact = models.CharField("Kontak pengirim", max_length=180)
    reward = models.CharField("Hadiah", max_length=160, blank=True)
    created_at = models.DateTimeField("Waktu terbit", auto_now_add=True, db_index=True)

    objects = SurveyQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "survei"
        verbose_name_plural = "survei"

    @property
    def expires_at(self):
        return self.created_at + SURVEY_LIFETIME

    def __str__(self):
        return self.title


def delete_expired_surveys():
    expired_surveys = Survey.objects.expired()
    if not expired_surveys.exists():
        return 0

    deleted_count, _ = expired_surveys.delete()
    return deleted_count
