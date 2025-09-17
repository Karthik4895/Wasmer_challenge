from django.db import models

class User(models.Model):
    HOBBY = 'H'
    PRO = 'P'
    PLAN_CHOICES = [(HOBBY, 'Hobby'), (PRO, 'Pro')]

    username = models.CharField(max_length=100, unique=True)
    plan = models.CharField(max_length=1, choices=PLAN_CHOICES, default=HOBBY)

    def __str__(self):
        return self.username

class DeployedApp(models.Model):
    owner = models.ForeignKey(User, related_name='apps', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"App #{self.id} for {self.owner.username}"
