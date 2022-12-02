from django import views
from django.urls import path
from django.contrib.auth import views as auth_view
from .views import register, addFoodItem,login_redirect
from django.contrib.auth import views as auth_view
from .views import indexPageView, createuserPageView, dashboardPageView, journalPageView, profilePageView, navView, searchFoodView,addFoodEntry, getAPIList, profilePageView, dashboardPageView, displayjournalPageView, submitFoodItem, addWaterEntry, submitWaterEntry, editWaterEntry, deleteWaterEntry, submitWaterChanges, deleteFoodEntry, editFoodEntry, foodChanges

from .views import indexPageView, createuserPageView, journalPageView, profilePageView, navView, searchFoodView,addFoodEntry, getAPIList, profilePageView, dashboardPageView, displayjournalPageView, submitFoodItem, addWaterEntry, submitWaterEntry, editWaterEntry, deleteWaterEntry, updateProfile

urlpatterns = [
    path('', indexPageView, name='index'),
    path('adddata/', getAPIList, name="data"),
    path('profile/', profilePageView, name='profile'),
    path('journal/', journalPageView, name='journal'),
    path('login/', auth_view.LoginView.as_view(template_name = 'login.html'), name='login'),
    path('logout/', auth_view.LogoutView.as_view(template_name = 'index.html'), name='logout'),
    path('createuser/', createuserPageView, name='createuser'),
    path('dashboard/', dashboardPageView, name='dashboard'),
    path('nav/', navView, name='nav'),
    path('journal/searchfood/', searchFoodView, name='searchfood'),
    path('displayjournal/', displayjournalPageView, name='displayjournal'),
    path('register/', register, name='register'),
    path('login_redirect', login_redirect, name='redirect'),
    path('addfood/', addFoodItem, name='addfood'),
    path('submitfood/', submitFoodItem, name='submitfood'),
    path('addwater/', addWaterEntry, name='addwater'),
    path('submitwater/', submitWaterEntry, name='submitwater'),
    path('editwater/<int:id>/', editWaterEntry, name='editwater'),
    path('deletewater/<int:id>/', deleteWaterEntry, name='deletewater'),
    path('submitwaterchanges/<int:id>/', submitWaterChanges, name="submitwater"),
    path('addentry/', addFoodEntry, name='addfoodentry'),
    path('deletefood/<int:id>/', deleteFoodEntry, name='deletefood'),
    path('editfood/<int:id>/', editFoodEntry, name='editfood'),
    path('foodchanges/<int:id>/', foodChanges, name='foodchanges'),
    path('updateprofile', updateProfile, name='update')
    ]

