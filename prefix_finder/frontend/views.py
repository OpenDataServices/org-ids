import os
import json
import glob

from django.shortcuts import render


current_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(current_dir, '../../data')

files = ['jurisdictions', 'organisation_types', 'sectors', 'subnational']

lists = {}

for file in files:
    with open(os.path.join(data_dir, file) + '.json') as data:
        lists[file] = json.load(data)

lists['jurisdictions'].sort(key=lambda k: k.get('country') or k.get('countryCode'))
lists['organisation_types'].sort(key=lambda k: k.get('name') or '')

codes_dir = os.path.join(current_dir, '../../codes')

prefixes = []
for prefix_file_name in glob.glob(codes_dir + '/*/*.json'):
    with open(prefix_file_name) as prefix_file:
        prefixes.append(json.load(prefix_file))

lists['prefix_list'] = prefixes



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
    prefix['jurisdiction_flat'] = [jurisdiction['countryCode'] for jurisdiction in prefix.get('jurisdiction') or []]


def filter_and_score_results(query):
    indexed = {prefix['code']: prefix.copy() for prefix in lists['prefix_list']}
    for prefix in list(indexed.values()):
        prefix['quality'] = 1
        prefix['relevence'] = 0
        register_type = prefix.get('registerType')
        if register_type and register_type == 'Primary':
            prefix['quality'] = 2

    jurisdiction = query.get('jurisdiction')
    if jurisdiction:
        for prefix in list(indexed.values()):
            if prefix['jurisdiction_flat']:
                if jurisdiction in prefix['jurisdiction_flat']:
                    prefix['relevence'] = prefix['relevence'] + 1
                else:
                    indexed.pop(prefix['code'])

    organisation_type = query.get('organisation_type')
    if organisation_type:
        for prefix in list(indexed.values()):
            if prefix['structure_flat']:
                if organisation_type in prefix['structure_flat']:
                    prefix['relevence'] = prefix['relevence'] + 1
                else:
                    indexed.pop(prefix['code'])
            else:
                indexed.pop(prefix['code'])
            
    sector = query.get('sector')
    if sector:
        for prefix in list(indexed.values()):
            if prefix['sector']:
                if sector == prefix.get('sector'):
                    prefix['relevence'] = prefix['relevence'] + 1
            else:
                indexed.pop(prefix['code'])


    all_results = {"suggested": [],
                   "recommended": [],
                   "other": []}

    if not indexed:
        return all_results

    top_relevence = max(prefix['relevence'] for prefix in indexed.values())
                   
    for value in sorted(indexed.values(), key=lambda k: -(k['relevence'] * 100 + k['quality'])):
        if value['relevence'] == top_relevence:
            all_results['suggested'].append(value)
        elif value['relevence'] == 0:
            all_results['other'].append(value)
        else:
            all_results['recommended'].append(value)

    return all_results


def home(request):
    query = {key: value[0] for key, value in dict(request.GET).items()
             if key in ['jurisdiction', 'organisation_type', 'sector']}
    context = {
        "lists": lists,
        "query": query
    }
    if query:
        context['all_results'] = filter_and_score_results(query)
         
    return render(request, "home.html", context=context)
