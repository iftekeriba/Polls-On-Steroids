import datetime
from django.db import models
from django.utils import timezone

class Poll(models.Model):
    def __str__(self):
        return self.question
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
    question = models.CharField(max_length=100)
    pub_date = models.DateTimeField('date published')

class Choice(models.Model):
    def __str__(self):
        return self.choice_text
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)
