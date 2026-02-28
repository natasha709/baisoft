from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='business_name_snapshot',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
