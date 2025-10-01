from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Recipient",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("full_name", models.CharField(max_length=255)),
                ("comment", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="recipients", to="auth.user")),
            ],
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("subject", models.CharField(max_length=255)),
                ("body", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="messages", to="auth.user")),
            ],
        ),
        migrations.CreateModel(
            name="Mailing",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start_at", models.DateTimeField()),
                ("end_at", models.DateTimeField()),
                ("status", models.CharField(choices=[("CREATED", "Создана"), ("RUNNING", "Запущена"), ("FINISHED", "Завершена")], default="CREATED", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("message", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="mailings", to="Message")),
                ("owner", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="mailings", to="auth.user")),
                ("recipients", models.ManyToManyField(related_name="mailings", to="Recipient")),
            ],
        ),
        migrations.CreateModel(
            name="MailAttempt",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("attempted_at", models.DateTimeField(auto_now_add=True)),
                ("status", models.CharField(choices=[("SUCCESS", "Успешно"), ("FAILED", "Не успешно")], max_length=20)),
                ("response", models.TextField(blank=True)),
                ("mailing", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="attempts", to="Mailing")),
                ("recipient", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="attempts", to="Recipient")),
                ("owner", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="attempts", to="auth.user")),
            ],
        ),
    ]