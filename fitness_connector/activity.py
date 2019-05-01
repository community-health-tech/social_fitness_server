from datetime import timedelta
from dateutil import parser
from dateutil.rrule import rrule, DAILY
from django.db.models import Sum
from django.utils import timezone
from fitbit.api import Fitbit
from fitness.models import ActivityByMinute, ActivityByDay
from fitness_connector.device import Device
from fitness_connector.models import Account
from fitness_connector import settings as fitbit_settings

RES_ID_STEPS = "activities/steps"
RES_ID_CALORIES = "activities/calories"
RES_ID_DISTANCE = "activities/distance"
RES_IDS_INTRADAY = [
    RES_ID_STEPS,
    RES_ID_CALORIES,
    RES_ID_DISTANCE,
]
KEY_INTRA_STEPS = "activities-steps-intraday"
KEY_INTRA_CALORIES = "activities-calories-intraday"
KEY_INTRA_DISTANCE = "activities-distance-intraday"
KEY_BASE_DATE = "today"
KEY_DETAIL_LEVEL = "1min"
TIME_START_OF_DAY = "00:00"
TIME_END_OF_DAY = "23:59"
DATETIME_ONE_DAY = timedelta(days=1)


class PersonActivity(object):
    """
    Manages a person's fitbit activity
    """
    
    def __init__(self, person_id):
        """
        Return the object whose person_id is *person_id*
        """
        self.person_id = person_id
        self.account = Account.objects.get(person__pk=person_id)
        self.fitbit = Fitbit (
            fitbit_settings.CLIENT_ID, 
            fitbit_settings.CLIENT_SECRET,
            access_token = self.account.access_token,
            refresh_token = self.account.refresh_token,
            expires_at = self.account.get_expires_at(),
            refresh_cb = self._refresh_cb,
        )
        self.device = None

    def pull_recent_data(self):
        """
        Pull the person's data since the last pull and save to database
        """
        self.device = Device(self.fitbit, self.account)
        self._pull_intraday_data(
            self.account.last_pull_time, 
            self.device.last_sync_time
        )
        return self.device.last_sync_time
    
    def _pull_intraday_data(self, start_datetime, end_datetime):
        """
        Given a start and end datetimes, pull data from Fitbit and
        save to database
        """
        dates = self._get_list_of_dates(start_datetime, end_datetime)

        for date in dates:
            self._pull_one_day_intraday_data(
                date['date'],
                date['start_time'],
                date['end_time']
            )
                
    def _pull_one_day_intraday_data(self, date_string, start_time, end_time):
        """
        Given a date plus start and end time, pull activities data and save
        them to database
        """
        one_day_data = {}
        for key in RES_IDS_INTRADAY:
            one_day_data[key] = self.fitbit.intraday_time_series(
                key,
                base_date = date_string,
                detail_level = KEY_DETAIL_LEVEL,
                start_time = start_time,
                end_time = end_time,
            )

        # self._save_one_day_data(date_string, one_day_data)
        self._save_one_day_intraday_data(date_string, one_day_data)
        self._update_one_day_data(date_string)

        # TODO this may introduce bugs
        self.account.last_pull_time = self.device.last_sync_time
        self.account.save()
        
        return(1)

    # def _save_one_day_data(self, date_string, one_day_data):
    #     try:
    #         one_day_activity = ActivityByDay.objects.get(
    #             date = self._get_tz_aware(date_string),
    #             person_id=self.account.person_id
    #         )
    #     except ActivityByDay.DoesNotExist:
    #         one_day_activity = ActivityByDay(
    #             date = self._get_tz_aware(date_string),
    #             person_id = self.account.person_id
    #         )
    #
    #     one_day_activity.steps += one_day_data[RES_ID_STEPS]["activities-steps"][0]["value"]
    #     one_day_activity.calories += one_day_data[RES_ID_CALORIES]["activities-calories"][0]["value"]
    #     one_day_activity.active_minutes += 0
    #     one_day_activity.distance += one_day_data[RES_ID_DISTANCE]["activities-distance"][0]["value"]
    #
    #     one_day_activity.save()

    def _save_one_day_intraday_data(self, date_string, one_day_data):
        step_data = self._get_dataset(one_day_data, RES_ID_STEPS, KEY_INTRA_STEPS)
        calorie_data = self._get_dataset(one_day_data, RES_ID_CALORIES, KEY_INTRA_CALORIES)
        distance_data = self._get_dataset(one_day_data, RES_ID_DISTANCE, KEY_INTRA_DISTANCE)

        activities_1m_in_1d = list()
        for steps, cals, dist in zip(step_data, calorie_data, distance_data):
            activity_1m = self._get_activity_1m(date_string, steps, cals, dist)
            activities_1m_in_1d.append(activity_1m)

        ActivityByMinute.objects.bulk_create(activities_1m_in_1d)

    def _update_one_day_data(self, date_string):
        date_tz_aware = self._get_tz_aware(date_string)
        try:
            one_day_activity = ActivityByDay.objects.get(
                date = date_tz_aware,
                person_id=self.account.person_id
            )
        except ActivityByDay.DoesNotExist:
            one_day_activity = ActivityByDay(
                date = date_tz_aware,
                person_id = self.account.person_id
            )

        one_day_aggregate = ActivityByMinute.objects\
            .filter(person_id=self.account.person_id, date=date_tz_aware)\
            .aggregate(total_steps=Sum('steps'),
                       total_calories=Sum('calories'),
                       total_distance=Sum('distance'))

        one_day_activity.steps = one_day_aggregate['total_steps']
        one_day_activity.calories = one_day_aggregate['total_calories']
        one_day_activity.active_minutes = 0
        one_day_activity.distance = one_day_aggregate['total_distance']
        one_day_activity.save()

    def _get_activity_1m(self, activity_date, steps, calories, distance):
        activity = ActivityByMinute(
            date=self._get_tz_aware(activity_date),
            time=self._get_tz_aware(steps["time"]),
            person_id=self.account.person_id
        )
        activity.steps = steps["value"]
        activity.calories = calories["value"]
        activity.level = calories["level"]
        activity.distance = distance["value"]
        return activity
        
    def _refresh_cb(self, token):
        """ Called when the OAuth token has been refreshed """
        self.account.access_token = token['access_token']
        self.account.refresh_token = token['refresh_token']
        self.account.set_expires_at_in_unix(token['expires_at'])
        self.account.save()

    @staticmethod
    def _get_list_of_dates(start_datetime, end_datetime):
        """
        :param start_datetime: the start datetime to pull
        :param end_datetime: the end datetime to pull
        :return: a list of dates to pull
        INVARIANT: start_datetime is always before end_datetime
        """
        dates = list()
        for date in rrule(DAILY, dtstart=start_datetime, until=end_datetime):
            dates.append({
                'date': date.strftime("%Y-%m-%d"),
                'start_time': date.strftime("%H:%M"),
                'end_time': TIME_END_OF_DAY
            })

        dates[0]['start_time'] = PersonActivity._get_hour_mins(start_datetime) if len(dates) > 1 else TIME_START_OF_DAY
        dates[len(dates) - 1]['end_time'] = PersonActivity._get_hour_mins(end_datetime)

        return dates

    @staticmethod
    def _get_dataset(data, key, response_key):
        return data[key][response_key]["dataset"]

    @staticmethod
    def _get_value(data, key, response_key):
        return data[key][response_key]["value"]

    @staticmethod
    def _get_hour_mins (datetime):
        return datetime.strftime("%H:%M")

    @staticmethod
    def _get_tz_datetime(activity_date, activity_time):
        activity_datetime = parser.parse(activity_date + " " + activity_time)
        return timezone.make_aware(activity_datetime,
            timezone.get_current_timezone())

    @staticmethod
    def _get_tz_aware(datetime_string):
        datetime = parser.parse(datetime_string)
        return timezone.make_aware(datetime, timezone.get_current_timezone())