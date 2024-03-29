import datetime
from django.db import models
from django.utils import timezone

class Poll(models.Model):
    def __str__(self):
        return self.question
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date < now
    question = models.CharField(max_length=100)
    pub_date = models.DateTimeField('date published')
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

class Choice(models.Model):
    def __str__(self):
        return self.choice_text
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)
