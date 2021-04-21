from django import template
from django.contrib.auth.models import User
from stock.models import BillOfMaterials, Profile
from stock.views import getUserCompany

register = template.Library()


@register.simple_tag
def relative_url(value, field_name, urlencode=None):
    url = '?{}={}'.format(field_name, value)
    if urlencode:
        querystring = urlencode.split('&')
        filtered_querystring = filter(lambda p: p.split('=')[0] != field_name, querystring)
        encoded_querystring = '&'.join(filtered_querystring)
        url = '{}&{}'.format(url, encoded_querystring)
    return url


@register.filter
def monify(monefy):
    if not monefy:
        return '0.00'
    monefy = format(monefy / 100., ',.2f')
    return monefy


@register.filter
def get_type(value):
    print(type(value))
    return str(type(value))


@register.filter
def get_username(value):
    username = User.objects.get(id=value)
    return username.username