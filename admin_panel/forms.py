from django import forms
from .models import ActivityLog
from fees.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class LogActionForm(forms.Form):
    ACTION_TYPE_CHOICES = [
        ('activity', 'Log Activity'),
        ('notification', 'Send Notification to Students'),
    ]
    action_type = forms.ChoiceField(choices=ACTION_TYPE_CHOICES, widget=forms.RadioSelect)
    action = forms.CharField(max_length=255, required=False, label="Activity Title/Notification Title")
    details = forms.CharField(widget=forms.Textarea, required=False, label="Details/Message")
    recipient = forms.ModelChoiceField(queryset=User.objects.filter(role='student'), required=False, label="Recipient (optional, leave blank for all students)")

    def clean(self):
        cleaned_data = super().clean()
        action_type = cleaned_data.get('action_type')
        if action_type == 'activity' and not cleaned_data.get('action'):
            self.add_error('action', 'Activity title is required.')
        if action_type == 'notification' and not cleaned_data.get('details'):
            self.add_error('details', 'Notification message is required.')
        return cleaned_data
