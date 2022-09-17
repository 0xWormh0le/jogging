from django.db import models
from django.db.models import Sum, Avg, Min, Max
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import UserManager as AuthUserManager, User as AuthUser
from django.utils.functional import cached_property
from datetime import date, timedelta
from math import ceil


class UserQuerySet(models.QuerySet):
    def filter_by_user(self, user):
        user = User.objects.get(pk=user.pk)
        if user.is_admin:
            return self
        if user.is_manager:
            return self.filter(is_superuser=False)
        else:
            return self.filter(pk=user.pk)


class UserManager(AuthUserManager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)


class User(AuthUser):
    USERNAME_FIELD = 'email'

    objects = UserManager()
    class Meta:
        proxy = True

    @cached_property
    def is_admin(self):
        return self.is_superuser

    @cached_property
    def is_manager(self):
        return self.is_staff and not self.is_superuser

    @cached_property
    def is_user(self):
        return not self.is_staff

    @cached_property
    def role(self):
        if self.is_admin:
            return 'admin'
        if self.is_manager:
            return 'manager'
        return 'user'

    def get_report(self, date_from, date_to):
        qs = self.records.all()
        if date_from is not None:
            qs = qs.filter(date_recorded__gte=date_from)
        if date_to is not None:
            qs = qs.filter(date_recorded__lte=date_to)

        agg_res = qs.aggregate(
            total_distance=Sum('distance'),
            total_duration=Sum('duration'),
            first_date_recorded=Min('date_recorded'),
            last_date_recorded=Max('date_recorded')
        )
        total_distance = agg_res['total_distance'] or 0
        total_duration = agg_res['total_duration'] or 1
        first_date_recorded = agg_res['first_date_recorded'] or date.today()
        last_date_recorded = agg_res['last_date_recorded'] or date.today()

        week_start = first_date_recorded.isocalendar()[1] + first_date_recorded.isocalendar()[0] * 366
        week_end = last_date_recorded.isocalendar()[1] + last_date_recorded.isocalendar()[0] * 366
        sums = {}
        for week in range(week_start, week_end + 1):
            sums[week] = {
                'distance': 0,
                'duration': 0
            }

        for item in qs:
            isocal = item.date_recorded.isocalendar()
            week = isocal[1] + isocal[0] * 366
            sums[week]['distance'] += item.distance
            sums[week]['duration'] += item.duration

        weekly = []
        for week in range(week_start, week_end + 1):
            if sums[week]['distance'] != 0 and sums[week]['duration'] != 0:
                week_of_year = week % 366
                year = int(week / 366)
                first_date_of_year = date(year, 1, 1)
                first_week_day_of_year = first_date_of_year - timedelta(first_date_of_year.isocalendar()[2] - 1)
                week_start = first_week_day_of_year + timedelta(weeks=week_of_year)
                weekly.append({
                    'distance': sums[week]['distance'],
                    'avg_speed': sums[week]['distance'] / sums[week]['duration'],
                    'from': week_start,
                    'to': week_start + timedelta(days=6)
                })

        date_diff = (last_date_recorded - first_date_recorded).days + 1
        weeks = ceil(date_diff / 7) or 1

        return {
            'avg_speed': total_distance / total_duration,
            'distance_per_week': total_distance / weeks,
            'weekly': weekly
        }
