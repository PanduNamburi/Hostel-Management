from django import forms
from .models import Attendance

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'total_periods', 'absent_periods', 'marked_by', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-700 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm dark:bg-gray-800', 'rows': 2}),
        }

class BulkAttendanceForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-700 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm dark:bg-gray-800'
    }))

    def __init__(self, *args, students=None, **kwargs):
        super().__init__(*args, **kwargs)
        if students:
            for student in students:
                # Total Periods Held
                self.fields[f'total_held_{student.id}'] = forms.IntegerField(
                    initial=8,
                    min_value=0,
                    widget=forms.NumberInput(attrs={
                        'class': 'appearance-none rounded-xl relative block w-full px-4 py-2 bg-gray-50 dark:bg-gray-900/40 border-0 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500',
                        'placeholder': 'Total'
                    })
                )
                # Periods Actually Attended
                self.fields[f'attended_{student.id}'] = forms.IntegerField(
                    initial=8,
                    min_value=0,
                    widget=forms.NumberInput(attrs={
                        'class': 'appearance-none rounded-xl relative block w-full px-4 py-2 bg-gray-50 dark:bg-gray-900/40 border-2 border-indigo-500/20 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500',
                        'placeholder': 'Attended'
                    })
                )
                self.fields[f'notes_{student.id}'] = forms.CharField(
                    required=False,
                    widget=forms.Textarea(attrs={
                        'class': 'appearance-none rounded-xl relative block w-full px-4 py-2 bg-gray-50 dark:bg-gray-900/40 border-0 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500',
                        'rows': 1,
                        'placeholder': 'Optional notes...'
                    })
                ) 