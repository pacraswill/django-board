from django import forms
from .models import Topic


class NewTopicForm(forms.ModelForm):
    # message 不在 Topic 表中，所以要单独写出来写出来
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'What is on your mind?'}
        ),
        max_length=4000,
        help_text='The max length of the text is 4000.')

    class Meta:
        model = Topic
        fields = ['subject', 'message']
