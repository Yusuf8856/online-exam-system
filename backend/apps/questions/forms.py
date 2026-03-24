from django import forms
from django.core.exceptions import ValidationError
from .models import Question

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'marks', 'option1', 'option2', 'option3', 'option4', 'answer']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
    def clean_answer(self):
        # Ensure the provided answer matches one of the options.
        answer = self.cleaned_data.get('answer')
        option1 = self.cleaned_data.get('option1')
        option2 = self.cleaned_data.get('option2')
        option3 = self.cleaned_data.get('option3')
        option4 = self.cleaned_data.get('option4')
        options = [option1, option2, option3, option4]

        if answer and answer not in options:
            raise ValidationError("The correct answer must exactly match one of the provided options (A, B, C, or D).")
        return answer