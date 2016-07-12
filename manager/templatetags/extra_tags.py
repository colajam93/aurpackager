from django import template
import lib.aur

register = template.Library()


@register.simple_tag
def aur_package_url(name):
    return lib.aur.aur_package_url(name)
