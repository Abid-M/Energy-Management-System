from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('homepage/', views.homepage, name='homepage'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('appliances/', views.appliances, name='appliances'),
    path('api/appliances/<int:appliance_id>',
         views.manage_appliances, name='manageappliances'),
    path('get_appliances/<str:month>/<str:type>',
         views.switch_appliances, name='get_appliances'),
    path('usage/', views.usage, name='usage'),
    path('budget/', views.budget, name='budget'),
    # change tis when i add views.comparison
    path('comparison/', views.comparison, name='comparison'),
    path('forum/', views.forum, name='forum'),
    path('post/<int:id>', views.post, name='post'),
]
