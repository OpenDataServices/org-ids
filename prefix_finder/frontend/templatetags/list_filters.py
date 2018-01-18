from django import template

register = template.Library()


@register.filter(name='split_examples')
def split_examples(value, arg):
    return value.replace(" ","").split(arg)