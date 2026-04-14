from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'role', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none rounded-xl relative block w-full px-4 py-3 bg-gray-50 dark:bg-gray-900/40 border-0 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 placeholder-gray-400 sm:text-sm transition-all duration-200 shadow-sm'

    def save(self, commit=True):
        user = super().save(commit=False)
        if user.role == CustomUser.Role.STUDENT:
            user.is_approved = True
        else:
            user.is_approved = False
        if commit:
            user.save()
        return user

class CustomUserChangeForm(forms.ModelForm):
    password = None  # Remove password field from the form
    
    class Meta:
        model = CustomUser
        fields = ('email', 'phone_number', 'profile_picture')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-700 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm dark:bg-gray-800' 