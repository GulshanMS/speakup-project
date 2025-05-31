from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model

class User(AbstractUser):
    ROLE_CHOICES = (
        ('whistleblower', 'Whistleblower'), #Regular user
        ('supervisor', 'Supervisor'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


User = get_user_model()

class UserIssue(models.Model):
    CATEGORY_CHOICES = [
        ('harassment', 'Harassment'),
        ('safety', 'Safety Concern'),
        ('management', 'Management Issue'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_emergency = models.BooleanField(default=False)  # NLP will set this later

    def __str__(self):
        return self.title


class VoteTopic(models.Model):
    question = models.CharField(max_length=255)
    choice_texts = models.TextField(help_text="Comma-separated choices (e.g., Yes,No,Maybe)")
    is_active = models.BooleanField(default=True)
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def is_expired(self):
        return self.deadline and timezone.now() > self.deadline

    def get_choices(self):
        return [choice.strip() for choice in self.choice_texts.split(',') if choice.strip()]

    def __str__(self):
        return self.question

class AnonymousMessage(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Suggestion(models.Model):
    topic = models.ForeignKey(VoteTopic, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=100)

    def __str__(self):
        return f"Suggestion for {self.topic or 'General'}"

class Choice(models.Model):
    topic = models.ForeignKey(VoteTopic, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class Vote(models.Model):
    topic = models.ForeignKey(VoteTopic, on_delete=models.CASCADE)
    choice = models.CharField(max_length=100)
    session_key = models.CharField(max_length=100)  # For anonymous tracking
    justification = models.TextField(blank=True)  # New justification field
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.choice} on '{self.topic}'"
