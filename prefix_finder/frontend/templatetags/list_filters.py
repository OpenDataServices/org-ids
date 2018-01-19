from django import template

register = template.Library()


@register.filter(name='split_examples')
def split_examples(value, arg):
    return value.replace(" ","").split(arg)


@register.filter
def split_on(value, arg):
    return value.split(arg)
