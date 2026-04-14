from django import forms
from .models import ActivityLog
from fees.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class LogActionForm(forms.Form):
    ACTION_TYPE_CHOICES = [
        ('activity', 'Official Announcement (Visible to all students)'),
        ('notification', 'Direct Notification (To a specific student or all students)'),
    ]
    action_type = forms.ChoiceField(choices=ACTION_TYPE_CHOICES, widget=forms.RadioSelect)
    action = forms.CharField(max_length=255, required=False, label="Title")
    details = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, label="Message / Description")
    recipient = forms.ModelChoiceField(queryset=User.objects.filter(role='student'), required=False, label="Recipient (optional, leave blank for all students)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white'})
            elif not isinstance(field.widget, forms.RadioSelect) and not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'})

    def clean(self):
        cleaned_data = super().clean()
        action_type = cleaned_data.get('action_type')
        if action_type == 'activity' and not cleaned_data.get('action'):
            self.add_error('action', 'Activity title is required.')
        if action_type == 'notification' and not cleaned_data.get('details'):
            self.add_error('details', 'Notification message is required.')
        return cleaned_data
