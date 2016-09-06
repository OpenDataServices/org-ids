import os
import json

from django.shortcuts import render


current_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(current_dir, '../../data')

files = ['jurisdictions', 'organisation_types', 'prefix_list', 'sectors', 'subnational']

lists = {}

for file in files:
    with open(os.path.join(data_dir, file) + '.json') as data:
        lists[file] = json.load(data)

lists['jurisdictions'].sort(key=lambda k: k.get('country') or k.get('country_code'))
lists['organisation_types'].sort(key=lambda k: k.get('name') or '')


def flatten_structure(structure):
    if isinstance(structure, dict):
        for key, value in structure.items():
            if key == 'name':
                yield value
            if isinstance(value, dict):
                yield from flatten_structure(value)

#make_prefix_list_more_searchable by flattening some fields
for prefix in lists['prefix_list']:
    structure_flat = []
    for item in prefix['structure'] or []:
        structure_flat.extend(list(flatten_structure(item)))
    prefix['structure_flat'] = structure_flat
    prefix['jurisdiction_flat'] = [jurisdiction['country_code'] for jurisdiction in prefix['jurisdiction']]


def home(request):
    context = {
        "lists": lists,
        "query": {key: value[0] for key, value in dict(request.GET).items()
                  if key in ['jurisdiction', 'organisation_type', 'sector']}
    }
    return render(request, "home.html", context=context)
