from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Создает группу "Менеджеры" и присваивает кастомные права'

    def handle(self, *args, **options):
        managers_group, created = Group.objects.get_or_create(name='Менеджеры')
        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" создана'))

        # Присваиваем права
        permissions = [
            'mailings.can_view_recipient', 'mailings.can_add_recipient',
            'mailings.can_change_recipient', 'mailings.can_delete_recipient',
            'mailings.can_view_message', 'mailings.can_add_message',
            'mailings.can_change_message', 'mailings.can_delete_message',
            'mailings.can_view_mailing', 'mailings.can_add_mailing',
            'mailings.can_change_mailing', 'mailings.can_delete_mailing',
            'mailings.can_send_mailing', 'mailings.can_view_mailattempt',
        ]
        for perm_codename in permissions:
            try:
                perm = Permission.objects.get(codename=perm_codename.split('.')[-1])
                managers_group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Право {perm_codename} не найдено'))

        self.stdout.write(self.style.SUCCESS('Права присвоены группе "Менеджеры"'))