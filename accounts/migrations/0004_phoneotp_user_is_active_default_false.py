from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_alter_user_email"),
    ]

    operations = [
        migrations.CreateModel(
            name="PhoneOTP",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phone", models.CharField(max_length=20)),
                ("otp_code", models.CharField(max_length=6)),
                ("purpose", models.CharField(choices=[("register", "Register"), ("reset_password", "Reset Password")], default="register", max_length=30)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                ("is_used", models.BooleanField(default=False)),
                ("attempts", models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name="user",
            name="is_active",
            field=models.BooleanField(default=False),
        ),
    ]
