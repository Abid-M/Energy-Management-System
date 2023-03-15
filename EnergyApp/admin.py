from django.contrib import admin

# Register your models here.
from .models import UserProfile, EnergyProvider, Appliance, ApplianceUsage, Budget, ForumPost, ForumComment
admin.site.register(UserProfile)
admin.site.register(EnergyProvider)
admin.site.register(Appliance)
admin.site.register(ApplianceUsage)
admin.site.register(Budget)
admin.site.register(ForumPost)
admin.site.register(ForumComment)

