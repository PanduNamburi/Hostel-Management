from django import forms
from .models import FeeRecord

class FeeRecordForm(forms.ModelForm):
    class Meta:
        model = FeeRecord
        fields = ['student', 'fee_amount', 'due_date', 'status', 'payment_date']
