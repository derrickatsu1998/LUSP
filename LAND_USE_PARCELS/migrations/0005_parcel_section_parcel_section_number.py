# from django.db import migrations, models


# class Migration(migrations.Migration):

#     dependencies = [
#         ("LAND_USE_PARCELS", "0004_alter_otpcode_options_alter_otpcode_user_and_more"),
#     ]

#     operations = [
#         migrations.AddField(
#             model_name="parcel",
#             name="section",
#             field=models.CharField(blank=True, default="", help_text="Survey section or neighbourhood name.", max_length=100),
#         ),
#         migrations.AddField(
#             model_name="parcel",
#             name="section_number",
#             field=models.CharField(blank=True, default="", help_text="Survey section number.", max_length=50),
#         ),
#     ]


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("LAND_USE_PARCELS", "0004_alter_otpcode_options_alter_otpcode_user_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="parcel",
            name="section",
            field=models.CharField(blank=True, default="", help_text="Survey section or neighbourhood name.", max_length=100),
        ),
        migrations.AddField(
            model_name="parcel",
            name="section_number",
            field=models.CharField(blank=True, default="", help_text="Survey section number.", max_length=50),
        ),
    ]
