from django import forms
from .models import DSAQuestion

class DSAQuestionForm(forms.ModelForm):
    class Meta:
        model = DSAQuestion
        fields = ['question_text', 'difficulty', 'topic', 'answer']

class UserAnswerForm(forms.Form):
    user_answer = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}), label="Your Answer")