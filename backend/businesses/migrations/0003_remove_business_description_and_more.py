from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('businesses', '0002_user_invitation_sent_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='business',
            name='description',
        ),
        migrations.AddField(
            model_name='business',
            name='can_assign_roles',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='business',
            name='can_create_users',
            field=models.BooleanField(default=True),
        ),
    ]
