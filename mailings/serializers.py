from rest_framework import serializers
from .models import Recipient, Message, Mailing, MailAttempt


class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "owner")


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "owner")


class MailingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "owner")


class MailAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailAttempt
        fields = "__all__"
        read_only_fields = ("id", "attempted_at", "owner")
