
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User, Transactions
from django.contrib.auth.forms import AuthenticationForm

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone_number', 'user_name', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('phone_number', 'user_name', 'is_active', 'is_admin', 'is_superuser')

    def clean_password(self):
        return self.initial["password"]

class UserLoginForm(AuthenticationForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class CashoutForm(forms.Form):
    multiplier = forms.DecimalField(label='Cashout Multiplier', max_digits=10, decimal_places=2)

class TransactionsForm(forms.ModelForm):
    class Meta:
        model = Transactions
        fields = ['user', 'bet']