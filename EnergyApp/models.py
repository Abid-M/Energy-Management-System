from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class EnergyProvider(models.Model):
    name = models.CharField(max_length=100, unique=True, default="Other")
    elecDailyCharge = models.DecimalField(
        decimal_places=2, max_digits=10, default="0")
    gasDailyCharge = models.DecimalField(
        decimal_places=2, max_digits=10, default="0")
    elecPerKwh = models.DecimalField(
        decimal_places=2, max_digits=10, default="0")
    gasPerKwh = models.DecimalField(
        decimal_places=2, max_digits=10, default="0")

    def __str__(self):
        return str(self.name)


class UserProfile(models.Model):
    PROVIDER_CHOICES = [
        ("EDF", "EDF"),
        ("British Gas", "British Gas"),
        ("EON", "EON"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profiles', null=True, blank=True)
    dob = models.DateField()
    provider = models.ForeignKey(EnergyProvider, on_delete=models.CASCADE, max_length=20)

    def __str__(self):
        return str(self.user)


class Appliance(models.Model):
    applianceType = models.CharField(max_length=11)
    name = models.CharField(max_length=100, default="Other")
    wattage = models.IntegerField()
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.name}"


class ApplianceUsage(models.Model):
    appliance = models.ForeignKey(Appliance, on_delete=models.CASCADE)
    duration = models.DecimalField(decimal_places=2, max_digits=10)
    date = models.DateField(auto_now_add=False)

    def __str__(self):
        return f"{self.appliance.user} - {self.appliance.name}"


class Budget(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    month = models.CharField(max_length=50)

    dailyElecCostBudget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    weeklyElecCostBudget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    monthlyElecCostBudget = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)
    
    dailyGasCostBudget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    weeklyGasCostBudget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    monthlyGasCostBudget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)

    def __str__(self):
        return f"{self.user} - {self.month}"
    
class ForumPost(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    createdBy = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ForumComment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    createdBy = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body
