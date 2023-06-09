# Generated by Django 4.1.5 on 2023-03-12 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EnergyApp', '0002_alter_budget_dailyeleccostbudget_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget',
            name='dailyElecCostBudget',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='budget',
            name='dailyGasCostBudget',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='budget',
            name='monthlyGasCostBudget',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='budget',
            name='weeklyElecCostBudget',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='budget',
            name='weeklyGasCostBudget',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
    ]
