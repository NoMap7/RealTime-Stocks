from django import template

register = template.Library()

def get_key(map, key):
    return map.get(key, '')

register.filter('get_key', get_key)