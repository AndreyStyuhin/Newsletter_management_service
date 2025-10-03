from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from mailings.models import Mailing, MailAttempt

class Command(BaseCommand):
    help = 'Отправляет рассылку по ID'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int)

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']
        try:
            mailing = Mailing.objects.get(id=mailing_id)
        except Mailing.DoesNotExist:
            raise CommandError(f'Рассылка с ID {mailing_id} не найдена')

        recipients = mailing.recipients.all()
        message = mailing.message

        for recipient in recipients:
            try:
                send_mail(
                    subject=message.subject,
                    message=message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                MailAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status="SUCCESS",
                    response="OK",
                    owner=mailing.owner,
                )
            except Exception as e:
                MailAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status="FAILED",
                    response=str(e),
                    owner=mailing.owner,
                )

        if mailing.status == "CREATED":
            mailing.status = "RUNNING"
        if mailing.end_at and mailing.end_at < timezone.now():
            mailing.status = "FINISHED"
        mailing.save()

        self.stdout.write(self.style.SUCCESS(f'Рассылка {mailing_id} выполнена'))