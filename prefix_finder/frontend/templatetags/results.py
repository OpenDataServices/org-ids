from collections import OrderedDict
from django import template

register = template.Library()

# SKIP_KEYS = 'name url code structure'.split()
paths_display_name = OrderedDict((
    (('description', ), 'Description'),
    (('coverage', ), 'Coverage'),
    (('access', 'languages'), 'Languages'),
    (('registerType', ), 'Register type'),
    (('data', 'licenseStatus'), 'Data license Status'),
    (('data', 'licenseDetails'), 'Data license details'),
    (('data', 'dataAccessDetails'), 'Data access'),
    (('data', 'availability'), 'Data availability'),
    (('data', 'features'), 'Data features'),
    (('access', 'availableOnline'), 'Available online'),
    (('access', 'onlineAccessDetails'), 'Online Access Details'),
    (('access', 'publicDatabase'), 'Public Database'),
    (('access', 'guidanceOnLocatingIds'), 'Finding the identifiers'),
    (('access', 'exampleIdentifiers'), 'Example identifier(s)'),
    (('links', 'opencorporates'), 'Open Corporates page'),
    (('links', 'wikipedia'), 'Wikipedia page'),
    (('confirmed', ), 'Confirmed?'),
    (('sector', ), 'Sector'),
    (('subnationalCoverage', ), 'Sub-national'),
    (('meta', 'lastUpdated'), 'Last Updated'),
    (('deprecated', ), 'Deprecated'),
    (('formerPrefixes', ), 'AKA'),
    (('meta', 'source'), 'Source'),
    (('quality', ), 'Quality'),
    (('relevence', ), 'Relevance')
))


@register.filter(name='tidy_results')
def tidy_results(results):
    tidied_results = OrderedDict()
    for paths, display in paths_display_name.items():
        key_name = display
        info = results
        for path in paths:
            info = info[path]

        if not info:
            continue

        if isinstance(info, list):
            tidied_results[key_name] = ", ".join(info).replace('_', ' ')
        elif isinstance(info, dict):
            if 'en' in info:
                info = info['en']
                tidied_results[key_name] = info
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
