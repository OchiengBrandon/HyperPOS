from django.db import models

# Example model for future use
class Feature(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()