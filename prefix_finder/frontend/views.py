import os
import json
import glob

from django.shortcuts import render
from django.http import HttpResponse


current_dir = os.path.dirname(os.path.realpath(__file__))

##globals
lookups = None
org_id_lists = None


def load_files():
    schema_dir = os.path.join(current_dir, '../../schema')
    schemas = {}
    for file_path in glob.glob(schema_dir + '/*.json'):
        with open(file_path) as data:
            schemas[file_path.split('/')[-1].split(".")[0]] = json.load(data)

    return schemas



def create_codelist_lookups(schemas):

    lookups = {}

    lookups['coverage'] = [(item['code'], item['title']['en']) for item in schemas['codelist-coverage']['coverage']] 
    lookups['subnationalCoverage'] = [(item['code'], item['title']['en']) for item in schemas['codelist-coverage']['subnationalCoverage']] 

    lookups['structure'] = [(item['code'], item['title']['en']) for item in schemas['codelist-structure']['structure'] if not item['parent']] 
    lookups['substructure'] = [(item['code'], item['title']['en']) for item in schemas['codelist-structure']['structure'] if item['parent']] 

    lookups['sector'] = [(item['code'], item['title']['en']) for item in schemas['codelist-sector']['sector']] 

    return lookups



def load_org_id_lists():
    codes_dir = os.path.join(current_dir, '../../codes')

    org_id_lists = []
    for org_id_list_file in glob.glob(codes_dir + '/*/*.json'):
        with open(org_id_list_file) as org_id_list:
            org_id_lists.append(json.load(org_id_list))

    return org_id_lists


def refresh_data():
    global lookups 
    global org_id_lists 

    lookups = create_codelist_lookups(load_files())
    org_id_lists = load_org_id_lists()

refresh_data()

def filter_and_score_results(query):
    indexed = {org_id_list['code']: org_id_list.copy() for org_id_list in org_id_lists}
    for prefix in list(indexed.values()):
        prefix['quality'] = 1
        prefix['relevence'] = 0
        register_type = prefix.get('registerType')
        if register_type and register_type == 'primary':
            prefix['quality'] = 2

    coverage = query.get('coverage')
    if coverage:
        for prefix in list(indexed.values()):
            if prefix['coverage']:
                if coverage in prefix['coverage']:
                    prefix['relevence'] = prefix['relevence'] + 1
                else:
                    indexed.pop(prefix['code'])
    else:
        if not prefix['coverage']:
            prefix['relevence'] = prefix['relevence'] + 0.25


    structure = query.get('structure')
    if structure:
        for prefix in list(indexed.values()):
            if prefix['structure']:
                if structure in prefix['structure']:
                    prefix['relevence'] = prefix['relevence'] + 1
                else:
                    indexed.pop(prefix['code'])
            else:
                indexed.pop(prefix['code'])
            
    sector = query.get('sector')
    if sector:
        for prefix in list(indexed.values()):
            if prefix['sector']:
                if sector in prefix['sector']:
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


def update_lists(request):
    refresh_data()
    return HttpResponse("List Refreshed")


def home(request):
    query = {key: value[0] for key, value in dict(request.GET).items()
             if key in ['coverage', 'structure', 'sector']}
    context = {
        "org_id_lists": org_id_lists,
        "lookups": lookups,
        "query": query
    }
    if query:
        context['all_results'] = filter_and_score_results(query)
         
    return render(request, "home.html", context=context)
