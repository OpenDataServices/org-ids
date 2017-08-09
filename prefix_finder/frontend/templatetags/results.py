from collections import OrderedDict
from django import template

register = template.Library()

paths_display_name = OrderedDict((
    (('description', ), 'Description'),
    (('coverage_titles', ), 'Coverage'),
    (('subnationalCoverage_titles', ), 'Subnational'),
    (('listType', ), 'List type'),
    (('data', 'licenseStatus'), 'Data license status'),
    (('relevance', ), 'Relevance'),
    (('quality', ), 'Quality'),
    (('relevance_debug', ), 'Relevance Debug'),
))


paths_display_name_long = OrderedDict((
    (('data', 'licenseDetails'), 'Data license details'),
    # (('data', 'dataAccessDetails'), 'Data access'),
    (('data', 'availability'), 'Data availability'),
    (('data', 'features'), 'Data features'),
    (('access', 'availableOnline'), 'Available online'),
    (('access', 'languages'), 'Languages'),
    (('access', 'onlineAccessDetails'), 'Online access'),
    (('access', 'publicDatabase'), 'Public Database'),
    (('access', 'guidanceOnLocatingIds'), 'Finding identifiers'),
    (('access', 'exampleIdentifiers'), 'Example identifier(s)'),
    (('links', 'opencorporates'), 'Open Corporates page'),
    (('links', 'wikipedia'), 'Wikipedia page'),
    (('confirmed', ), 'Confirmed?'),
    (('sector', ), 'Sector'),
    (('meta', 'lastUpdated'), 'Last updated'),
    (('deprecated', ), 'Deprecated'),
    (('formerPrefixes', ), 'AKA'),
    (('meta', 'source'), 'Source'),
))


@register.filter(name='tidy_results')
def tidy_results(results, length=None):
    paths_display = OrderedDict(paths_display_name)
    if length == 'long':
        paths_display.update(paths_display_name_long)
    tidied_results = OrderedDict()
    for paths, display in paths_display.items():
        key_name = display
        info = results
        for path in paths:
            info = info.get(path)

        if not info:
            continue

        if isinstance(info, list):
            tidied_results[key_name] = ", ".join(info).replace('_', ' ')
        elif isinstance(info, dict):
            if 'en' in info:
                info = info['en']
                if info:
                    if key_name == 'Description':
                        if length == 'long':
                            continue
                        else:
                            info = info.split(". ")[0]  # (naively) shorten description
                    tidied_results[key_name] = '{}.'.format(info)
            else:
                for field_name, details in info.items():
                    if isinstance(details, list):
                        details = ", ".join(details).join(info).replace('_', ' ')
                    tidied_results[field_name] = details
        else:
            if isinstance(info, bool):
                info = 'Yes' if info else 'No'
            if isinstance(info, str) and '_' in info:
                info = info.replace('_', ' ')
            tidied_results[key_name] = info

    return tidied_results.items()


@register.filter
def join_with(value, conj):
    """Given a list of strings, format them with commas and spaces, but
    with 'and' or 'or' at the end.

    >>> join_with(['apples', 'oranges', 'pears'], 'and')
    "apples, oranges, and pears"
    """
    if not value:
        return ""
    if len(value) == 1:
        return value[0]

    # convert numbers to strings
    value = [str(item) for item in value]

    # join all but the last element
    all_but_last = ", ".join(value[:-1])
    return "%s %s %s" % (all_but_last, conj, value[-1])

@register.filter
def split_on(value, arg):
    return value.split(arg)
