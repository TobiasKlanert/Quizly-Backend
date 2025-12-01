from django.db import models

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.URLField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name="questions", on_delete=models.CASCADE)

    question_title = models.CharField(max_length=500)
    question_options = models.JSONField()  
    answer = models.CharField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_title
