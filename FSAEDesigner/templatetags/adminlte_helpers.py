from django import template
from django.conf import settings
from django.urls import reverse
register = template.Library()


@register.simple_tag()
def logout_url():
    return getattr(settings, 'LOGOUT_URL', '/logout/')


@register.simple_tag(takes_context=True)
def has_avatar(context, size=None, user=None):
    user = context['request'].user if user is None else user
    return True if user.avatar.name else False


@register.simple_tag(takes_context=True)
def avatar_url(context, size=None, user=None):
    # TODO: Make behaviour configurable
    user = context['request'].user if user is None else user
    return settings.MEDIA_URL + user.avatar.name


@register.simple_tag(takes_context=True)
def add_active(context, url_name, *args, **kwargs):
    exact_match = kwargs.pop('exact_match', False)
    not_when = kwargs.pop('not_when', '').split(',')
    not_when = [nw.strip() for nw in not_when if nw.strip()]

    path = reverse(url_name, args=args, kwargs=kwargs)
    current_path = context.request.path

    if not_when and any(nw in current_path for nw in not_when):
        return ''

    if not exact_match and current_path.startswith(path):
        return ' active '
    elif exact_match and current_path == path:
        return ' active '
    else:
        return ''
