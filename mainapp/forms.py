from django import forms
from django.forms import ModelForm
from .models import UserInfo
from .models import Actuals
from django.contrib.auth.models import User

 
class LoginForm(forms.ModelForm):
     class Meta:
         model = Actuals
         fields = '__all__'

class UserForm(ModelForm) :
    class Meta:
        model = UserInfo
        fields = ('FirstName', 'LastName', 'DOB', 'HeightFt', 'HeightIn', 'Weight', 'Sex')
        labels = {
            'FirstName': 'Name',
            'LastName': '',
            'DOB': 'Birthdate',
            'HeightFt': 'Height',
            'HeightIn': '',
            'Weight': 'Weight in lbs',
            'Sex': 'Sex'
        }
        widgets = {
            'FirstName': forms.TextInput(attrs={'placeholder':'First Name'}),
            'LastName': forms.TextInput(attrs={'placeholder':'Last Name'}),
            'DOB': forms.DateInput(attrs={'placeholder':'ie. 1995-12-31'}),
            'HeightFt': forms.NumberInput(attrs={'placeholder':'Feet'}),
            'HeightIn': forms.NumberInput(attrs={'placeholder':'Inches'}),
            'Weight': forms.NumberInput(attrs={'placeholder':'123'}),
            'Sex': forms.TextInput(attrs={'placeholder':'M/F'})
        }
# class LoginForm(ModelForm) :
#     class Meta:
#         model = User
#         fields = ('username', 'password')
