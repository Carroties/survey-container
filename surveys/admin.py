from django.contrib import admin

from .models import Survey


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ["title", "sender", "created_at"]
    search_fields = ["title", "sender"]
    readonly_fields = ["created_at"]
