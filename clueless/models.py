from django.db import models

#suggestion model specifically for skeletal increment (this will be modified/removed later)
class Suggestion(models.Model):
    user = models.CharField(max_length=150)
    text = models.CharField(max_length=500)

#accusation model specifically for skeletal increment (this will be modified/removed later)
class Accusation(models.Model):
    user = models.CharField(max_length=150)
    text = models.CharField(max_length=500)