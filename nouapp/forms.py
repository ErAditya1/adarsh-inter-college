from django import forms
from .models import StudentFee, FeesType,Period,TimetableEntry,SalaryStructure,SalaryPayment

class StudentFeeForm(forms.ModelForm):
    class Meta:
        model = StudentFee
        fields = ['fee_type', 'amount_paid', 'payment_method']
        widgets = {
            'fee_type': forms.Select(attrs={'class': 'w-full border p-2 rounded ' }),
            'amount_paid': forms.NumberInput(attrs={'class': 'w-full border p-2 rounded text-'}),
            'payment_method': forms.Select(attrs={'class': 'w-full border p-2 rounded'}),
        }
    def __init__(self, *args, **kwargs):
        student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)
        if student:
            self.fields['fee_type'].queryset = FeesType.objects.filter(
                school_class=student.school_class,
                section=student.section
            )


class PeriodForm(forms.ModelForm):
    class Meta:
        model = Period
        fields = ['name', 'start_time', 'end_time']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full p-2 border rounded'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full p-2 border rounded'}),
        }


class TimetableEntryForm(forms.ModelForm):
    class Meta:
        model = TimetableEntry
        fields = ['school_class', 'section', 'day', 'period', 'subject', 'teacher']
        widgets = {
            'school_class': forms.Select(attrs={'class': 'w-full p-2 border rounded','id':"school_class"}),
            'section': forms.Select(attrs={'class': 'w-full p-2 border rounded','id':'section'}),
            'day': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'period': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'subject': forms.Select(attrs={'class': 'w-full p-2 border rounded','id':'subject'}),
            'teacher': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
        }

class SalaryStructureForm(forms.ModelForm):
    class Meta:
        model = SalaryStructure
        fields = ['base_salary', 'bonuses', 'deductions', 'allowances', 'tax_percent']
        widgets={
            'base_salary':forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'bonuses':forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'deductions':forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'allowances':forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'tax_percent':forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
        }


class SalaryPaymentForm(forms.ModelForm):
    class Meta:
        model = SalaryPayment
        fields = ['worked_days', 'absent_days']
        widgets={
            'worked_days':forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'absent_days':forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
        }





   