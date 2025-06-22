from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class DSAQuestion(models.Model):
    question_text = models.TextField()
    difficulty = models.CharField(max_length=20)
    topic = models.CharField(max_length=100)
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text[:50]
    
class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(DSAQuestion, on_delete=models.CASCADE)
    user_answer = models.TextField()
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)