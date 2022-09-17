from django.db import models
from user.models import User

class RecordQuerySet(models.QuerySet):
    def filter_by_user(self, user):
        user = User.objects.get(pk=user.pk)
        if user.is_admin:
            return self
        if user.is_manager:
            return self.exclude(user__is_superuser=False)
        else:
            return self.filter(user=user)


class Record(models.Model):
    user = models.ForeignKey('user.User', related_name='records')
    date_recorded = models.DateField()
    distance = models.FloatField()
    duration = models.IntegerField()
    objects = RecordQuerySet.as_manager()

    def __str__(self):
        return '{} # {}'.format(self.user, self.date_recorded)
