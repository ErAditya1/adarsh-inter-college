from django import forms
from .models import StudentFee, FeesType

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
