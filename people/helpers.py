from django.http import Http404

from people.models import Person, Group


def get_group(user_id):
    try:
        person = Person.objects.get(user__id=user_id)
        return Group.objects.get(members=person)
    except Person.DoesNotExist:
        raise Http404
    except Group.DoesNotExist:
        raise Http404