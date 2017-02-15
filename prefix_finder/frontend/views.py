import os
import json
import glob

from django.shortcuts import render


current_dir = os.path.dirname(os.path.realpath(__file__))


def load_files():
    schema_dir = os.path.join(current_dir, '../../schema')
    schemas = {}
    for file_path in glob.glob(schema_dir + '/*.json'):
        with open(file_path) as data:
            schemas[file_path.split('/')[-1].split(".")[0]] = json.load(data)

    return schemas

schemas = load_files()


def create_codelist_lookups(schemas):

    lookups = {}

    lookups['coverage'] = [(item['code'], item['title']['en']) for item in schemas['codelist-coverage']['coverage']] 
    lookups['subnationalCoverage'] = [(item['code'], item['title']['en']) for item in schemas['codelist-coverage']['subnationalCoverage']] 

    lookups['structure'] = [(item['code'], item['title']['en']) for item in schemas['codelist-structure']['structure'] if not item['parent']] 
    lookups['substructure'] = [(item['code'], item['title']['en']) for item in schemas['codelist-structure']['structure'] if item['parent']] 

    lookups['sector'] = [(item['code'], item['title']['en']) for item in schemas['codelist-sector']['sector']] 

    return lookups

lookups = create_codelist_lookups(schemas)


def load_org_id_lists():
    codes_dir = os.path.join(current_dir, '../../codes')

    org_id_lists = []
    for org_id_list_file in glob.glob(codes_dir + '/*/*.json'):
        with open(org_id_list_file) as org_id_list:
            org_id_lists.append(json.load(org_id_list))

    return org_id_lists

org_id_lists = load_org_id_lists()

#import pprint; pprint.pprint(org_id_lists)

#def flatten_structure(structure):
    #if isinstance(structure, dict):
        #for key, value in structure.items():
            #if key == 'name':
                #yield value
            #if isinstance(value, dict):
                #yield from flatten_structure(value)

##make_prefix_list_more_searchable by flattening some fields
#for prefix in lists['prefix_list']:
    #structure_flat = []
    #for item in prefix['structure'] or []:
        #structure_flat.extend(list(flatten_structure(item)))
    #prefix['structure_flat'] = structure_flat
    #prefix['jurisdiction_flat'] = [jurisdiction['countryCode'] for jurisdiction in prefix.get('jurisdiction') or []]


def filter_and_score_results(query):
    indexed = {org_id_list['code']: org_id_list.copy() for org_id_list in org_id_lists}
    for prefix in list(indexed.values()):
        register_type = prefix.get('registerType')
        if register_type:
            if register_type == 'primary':
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
