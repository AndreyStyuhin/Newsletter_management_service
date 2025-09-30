from django.contrib import admin
from .models import Recipient, Message, Mailing, MailAttempt

@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "owner", "created_at")
    search_fields = ("email", "full_name")

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "owner", "created_at")
    search_fields = ("subject",)

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "start_at", "end_at", "owner")
    list_filter = ("status", "start_at", "end_at")

@admin.register(MailAttempt)
class MailAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "mailing", "recipient", "status", "attempted_at")
    list_filter = ("status", "attempted_at")
