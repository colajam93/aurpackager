from django import template

from lib.aur import package_url

register = template.Library()


@register.simple_tag
def aur_package_url(name: str, server: str) -> str:
    return package_url(aur_server_tag=server, package_name=name)
