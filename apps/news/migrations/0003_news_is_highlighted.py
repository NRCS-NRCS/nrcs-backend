from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0002_alter_news_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="news",
            name="is_highlighted",
            field=models.BooleanField(default=False),
        ),
    ]
