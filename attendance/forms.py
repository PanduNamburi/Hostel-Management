from django import forms
from .models import Attendance

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'total_periods', 'absent_periods', 'marked_by', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-700 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm dark:bg-gray-800', 'rows': 2}),
            'is_present': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 dark:border-gray-700 rounded dark:bg-gray-800'}),
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
                field_name = f'student_{student.id}'
                self.fields[field_name] = forms.BooleanField(
                    required=False,
                    initial=True,
                    label=student.get_full_name() or student.username,
                    widget=forms.CheckboxInput(attrs={
                        'class': 'h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 dark:border-gray-700 rounded dark:bg-gray-800'
                    })
                )
                self.fields[f'notes_{student.id}'] = forms.CharField(
                    required=False,
                    widget=forms.Textarea(attrs={
                        'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-700 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm dark:bg-gray-800',
                        'rows': 1,
                        'placeholder': 'Notes (optional)'
                    })
                ) 