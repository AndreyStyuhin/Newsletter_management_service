from django.db import models
from django.conf import settings


class Recipient(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipients"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    class Meta:
        permissions = [
            ("can_view_recipient", "Can view recipient"),
            ("can_add_recipient", "Can add recipient"),
            ("can_change_recipient", "Can change recipient"),
            ("can_delete_recipient", "Can delete recipient"),
        ]


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

    class Meta:
        permissions = [
            ("can_view_message", "Can view message"),
            ("can_add_message", "Can add message"),
            ("can_change_message", "Can change message"),
            ("can_delete_message", "Can delete message"),
        ]


class Mailing(models.Model):
    STATUS_CHOICES = [
        ("CREATED", "Создана"),
        ("RUNNING", "Запущена"),
        ("FINISHED", "Завершена"),
    ]

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="CREATED")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="mailings")
    recipients = models.ManyToManyField(Recipient, related_name="mailings")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mailings"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Mailing {self.id} ({self.get_status_display()})"

    class Meta:
        permissions = [
            ("can_view_mailing", "Can view mailing"),
            ("can_add_mailing", "Can add mailing"),
            ("can_change_mailing", "Can change mailing"),
            ("can_delete_mailing", "Can delete mailing"),
            ("can_send_mailing", "Can send mailing"),
        ]


class MailAttempt(models.Model):
    STATUS_CHOICES = [
        ("SUCCESS", "Успешно"),
        ("FAILED", "Не успешно"),
    ]

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name="attempts")
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name="attempts")
    attempted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    response = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attempts"
    )

    def __str__(self):
        return f"Attempt {self.id} — {self.get_status_display()}"

    class Meta:
        permissions = [
            ("can_view_mailattempt", "Can view mail attempt"),
        ]