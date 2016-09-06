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


def filter_and_score_results(query):
    indexed = {prefix['code']: prefix.copy() for prefix in lists['prefix_list']}
    for prefix in list(indexed.values()):
        register_type = prefix.get('register_type')
        if register_type:
            if register_type == 'Primary':
                prefix['weight'] = 4
            else:
                prefix['weight'] = 1
        else:
            prefix['weight'] = 1

    jurisdiction = query.get('jurisdiction')
    if jurisdiction:
        for prefix in list(indexed.values()):
            if prefix['jurisdiction_flat']:
                if jurisdiction in prefix['jurisdiction_flat']:
                    prefix['weight'] = prefix['weight'] * 10
                else:
                    indexed.pop(prefix['code'])

    organisation_type = query.get('organisation_type')
    if organisation_type:
        for prefix in list(indexed.values()):
            if prefix['structure_flat']:
                if organisation_type in prefix['structure_flat']:
                    prefix['weight'] = prefix['weight'] * 10
                else:
                    indexed.pop(prefix['code'])
            else:
                indexed.pop(prefix['code'])
            
    sector = query.get('sector')
    if sector:
        for prefix in list(indexed.values()):
            if prefix['sector']:
                if sector == prefix['structure_flat']:
                    prefix['weight'] = prefix['weight'] * 10
            else:
                indexed.pop(prefix['code'])

    return sorted(indexed.values(), key=lambda k: -k['weight'])


def home(request):
    query = {key: value[0] for key, value in dict(request.GET).items()
             if key in ['jurisdiction', 'organisation_type', 'sector']}
    context = {
        "lists": lists,
        "query": query
    }
    if query:
        context['results'] = filter_and_score_results(query)
         
    return render(request, "home.html", context=context)
