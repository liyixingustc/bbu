from django import forms
from django.contrib.auth.models import User

class SignUpForm(forms.Form):
    username = forms.CharField(required=True,max_length=100,label='Username')
    email=forms.EmailField(required=True,max_length=30,label='Email address')
    password = forms.CharField(required=True,min_length=8,max_length=30,label='Password')
    password_repeat = forms.CharField(required=True,min_length=8,max_length=30,label='Password(again)')
    company = forms.CharField(required=True,min_length=1,max_length=30, label='Company')

    def clean_username(self):
        user=User.objects.filter(username__iexact=self.cleaned_data['username'])
        if user.exists():
            raise forms.ValidationError("Username is used")
        return self.cleaned_data['username']

    def clean(self):
        if 'password' in self.cleaned_data :
            if 'password_repeat' in self.cleaned_data:
                if self.cleaned_data['password'] != self.cleaned_data['password_repeat']:
                    raise forms.ValidationError("The two password fields did not match.")
            else:
                raise forms.ValidationError('Password confirmation is invalid')
        else:
            raise forms.ValidationError('Password is invalid')

        return self.cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(required=True,max_length=100,label='Username')
    password = forms.CharField(required=True,max_length=30,label='Password')
    remember = forms.CharField(required=False,max_length=10,label='Remember')