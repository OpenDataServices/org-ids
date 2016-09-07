from django import template

register = template.Library()

SKIP_KEYS = '''name url code structure
               jurisdiction_flat structure_flat'''.split()

name_to_identifier = {"code": "code",
                      "name": "name",
                      "Description": "description",
                      "Jurisdiction": "jurisdiction",
                      "url": "url",
                      "Public Database": "public-database",
                      "Legal Structure": "structure",
                      "Example identifier(s)": "example_identifiers",
                      "Register Type": "register_type",
                      "Available online?": "available_online",
                      "Finding the identifiers": "guidance_on_locating_ids",
                      "Openly licensed": "license_status",
                      "License details": "license_details",
                      "Online availability": "online_access_details",
                      "Access to data": "data_access_properties",
                      "Data access details": "data_access_details",
                      "Data features": "dataset_features",
                      "In OpenCorporates?": "opencorporates",
                      "Languages supported": "languages",
                      "Sector": "sector",
                      "Sub-national": "subnational",
                      "Wikipedia page": "wikipedia",
                      "Confirmed?": "confirmed",
                      "Last Updated": "last_updated",
                      "Deprecated": "deprecated",
                      "AKA": "former_prefixes",
                      "Source": "source",
                      "Weight": "weight"}

identifier_to_name = dict((value, key) for key, value in name_to_identifier.items())


@register.filter(name='tidy_results')
def tidy_results(results):
    tidied_results = {}
    for key, value in results.items():
        key_name = identifier_to_name.get(key, key)
        if key == 'structure_flat':
            tidied_results[identifier_to_name['structure']] = ", ".join(value)
        if key in SKIP_KEYS:
            continue
        if value and isinstance(value, list):
            if isinstance(value[0], str):
                tidied_results[key_name] = ", ".join(value)
                continue
            if key == 'jurisdiction':
                tidied_results[key_name] = ", ".join('{country} ({country_code})'.format(**item) for item in value)
                continue
            if key == 'subnational':
                tidied_results[key_name] = ", ".join('{region_name} ({region_code})'.format(**item) for item in value)
                continue
            if key == 'sector':
                tidied_results[key_name] = ", ".join(item['name'] for item in value)
                continue
        tidied_results[key_name] = value
    return sorted(tidied_results.items())
