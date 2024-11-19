from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def del_session_message(context):
    request = context['request']
    if 'message' in request.session:
        del request.session['message']
    if 'alert' in request.session:
        del request.session['alert']
    return ''  
