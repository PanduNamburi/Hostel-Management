from django import forms
from .models import Complaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['title', 'description', 'priority', 'photo']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'appearance-none rounded-xl relative block w-full px-4 py-3 bg-gray-50 dark:bg-gray-900/40 border-0 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 placeholder-gray-400 sm:text-sm'}),
            'description': forms.Textarea(attrs={'class': 'appearance-none rounded-xl relative block w-full px-4 py-3 bg-gray-50 dark:bg-gray-900/40 border-0 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 placeholder-gray-400 sm:text-sm', 'rows': 4}),
            'priority': forms.Select(attrs={'class': 'appearance-none rounded-xl relative block w-full px-4 py-3 bg-gray-50 dark:bg-gray-900/40 border-0 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 sm:text-sm'}),
            'photo': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-black file:bg-indigo-50 file:text-indigo-600 hover:file:bg-indigo-100 dark:file:bg-indigo-900/30 dark:file:text-indigo-400 transition-all'}),
        } 