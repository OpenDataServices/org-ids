from django import template

register = template.Library()

SKIP_KEYS = '''name url code structure
               weight jurisdiction_flat structure_flat'''.split()


@register.filter(name='tidy_results')
def tidy_results(results):
    tidied_results = {}
    for key, value in results.items():
        if key == 'structure_flat':
            tidied_results['structure'] = ", ".join(value)
        if key in SKIP_KEYS:
            continue
        if value and isinstance(value, list):
            if isinstance(value[0], str):
                tidied_results[key] = ", ".join(value)
                continue
            if key == 'jurisdiction':
                tidied_results[key] = ", ".join('{country} ({country_code})'.format(**item) for item in value)
                continue
            if key == 'subnational':
                tidied_results[key] = ", ".join('{region_name} ({region_code})'.format(**item) for item in value)
                continue
        tidied_results[key] = value
    return sorted(tidied_results.items())
