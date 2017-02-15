from django import template

register = template.Library()

SKIP_KEYS = '''name url code structure
               jurisdiction_flat structure_flat'''.split()

name_to_identifier = {"code": "code",
                      "name": "name",
                      "Description": "description",
                      "Jurisdiction": "jurisdiction",
                      "url": "url",
                      "Public Database": "publicDatabase",
                      "Legal Structure": "structure",
                      "Example identifier(s)": "exampleIdentifiers",
                      "Register Type": "registerType",
                      "Available online?": "availableOnline",
                      "Finding the identifiers": "guidanceOnLocatingIds",
                      "Openly licensed": "licenseStatus",
                      "License details": "licenseDetails",
                      "Online availability": "onlineAccessDetails",
                      "Access to data": "dataAccessProperties",
                      "Data access details": "dataAccessDetails",
                      "Data features": "datasetFeatures",
                      "In OpenCorporates?": "opencorporates",
                      "Languages supported": "languages",
                      "Sector": "sector",
                      "Sub-national": "subnational",
                      "Wikipedia page": "wikipedia",
                      "Confirmed?": "confirmed",
                      "Last Updated": "lastUpdated",
                      "Deprecated": "deprecated",
                      "AKA": "formerPrefixes",
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
                tidied_results[key_name] = ", ".join('{country} ({countryCode})'.format(**item) for item in value)
                continue
            if key == 'subnational':
                tidied_results[key_name] = ", ".join('{regionName} ({regionCode})'.format(**item) for item in value)
                continue
        tidied_results[key_name] = value
    return sorted(tidied_results.items())
