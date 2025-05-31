from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserIssue, Suggestion

class UserRegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']



class UserIssueForm(forms.ModelForm):
    class Meta:
        model = UserIssue
        fields = ['title', 'description', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Issue title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your issue'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }


class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Type your anonymous suggestion here...',
                'class': 'form-control',
            }),
        }



#Supervisor Dashboard

# forms.py
from django import forms
from .models import VoteTopic, Choice

class VoteTopicForm(forms.ModelForm):
    class Meta:
        model = VoteTopic
        fields = ['question', 'description', 'is_active', 'deadline']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text']

