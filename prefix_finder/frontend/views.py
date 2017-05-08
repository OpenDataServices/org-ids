import os
import json
import glob
import zipfile
import io
import csv
from collections import OrderedDict

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings
import requests
import datetime

RELEVANCE = {
    "MATCH_DROPDOWN": 10,
    "MATCH_DROPDOWN_ONLY_VALUE": 10,
    "MATCH_EMPTY": 2,
    "RECOMENDED_RELEVANCE_THRESHOLD": 5,
    "SUGGESTED_RELEVANCE_THRESHOLD": 35,
    "SUGGESTED_QUALITY_THRESHOLD": 45
}

current_dir = os.path.dirname(os.path.realpath(__file__))

##globals
lookups = None
org_id_dict = None
git_commit_ref = ''


def load_schemas_from_github(branch="master"):
    schemas = {}
    response = requests.get("https://github.com/OpenDataServices/org-ids/archive/"+branch+".zip")
    with zipfile.ZipFile(io.BytesIO(response.content)) as ziped_repo:
        for filename in ziped_repo.namelist():
            filename_split = filename.split("/")[1:]
            if len(filename_split) == 2 and filename_split[0] == "schema" and filename_split[-1].endswith(".json"):
                with ziped_repo.open(filename) as schema_file:
                    schemas[filename_split[-1].split(".")[0]] = json.loads(schema_file.read().decode('utf-8'))
    return schemas


def load_schemas_from_disk():
    schemas = {}
    schema_dir = os.path.join(current_dir, '../../schema')
    for file_path in glob.glob(schema_dir + '/*.json'):
        with open(file_path) as data:
            schemas[file_path.split('/')[-1].split(".")[0]] = json.load(data)

    return schemas


def create_codelist_lookups(schemas):
    lookups = {}
    lookups['coverage'] = sorted(
        [(item['code'], item['title']['en']) for item in schemas['codelist-coverage']['coverage']],
        key=lambda tup: tup[1]
    )
    lookups['structure'] = [(item['code'], item['title']['en']) for item in schemas['codelist-structure']['structure'] if not item['parent']]
    lookups['sector'] = [(item['code'], item['title']['en']) for item in schemas['codelist-sector']['sector']]

    lookups['subnational'] = {}
    for item in schemas['codelist-coverage']['subnationalCoverage']:
        if lookups['subnational'].get(item['countryCode']):
            lookups['subnational'][item['countryCode']].append((item['code'], item['title']['en']))
        else:
            lookups['subnational'][item['countryCode']] = [(item['code'], item['title']['en'])]

    lookups['substructure'] = {}
    for item in schemas['codelist-structure']['structure']:
        if item['parent']:
            code_title = (item['code'], item['title']['en'].split(' > ')[1])
            if lookups['substructure'].get(item['parent']):
                lookups['substructure'][item['parent']].append(code_title)
            else:
                lookups['substructure'][item['parent']] = [code_title]

    return lookups


def load_org_id_lists_from_github():
    org_id_lists = []
    response = requests.get("https://github.com/OpenDataServices/org-ids/archive/master.zip")
    with zipfile.ZipFile(io.BytesIO(response.content)) as ziped_repo:
        for filename in ziped_repo.namelist():
            filename_split = filename.split("/")[1:]
            if len(filename_split) == 3 and filename_split[0] == "codes" and filename_split[-1].endswith(".json"):
                with ziped_repo.open(filename) as schema_file:
                    org_id_lists.append(json.loads(schema_file.read().decode('utf-8')))
    return org_id_lists


def load_org_id_lists_from_disk():
    codes_dir = os.path.join(current_dir, '../../codes')
    org_id_lists = []
    for org_id_list_file in glob.glob(codes_dir + '/*/*.json'):
        with open(org_id_list_file) as org_id_list:
            org_id_lists.append(json.load(org_id_list))

    return org_id_lists


def augment_quality(schemas, org_id_lists):
    availabilty_score = {item['code']: item['quality_score'] for item in schemas['codelist-availability']['availability']}
    availabilty_names = {item['code']: item['title']['en'] for item in schemas['codelist-availability']['availability']}
    license_score = {item['code']: item['quality_score'] for item in schemas['codelist-licenseStatus']['licenseStatus']}
    license_names = {item['code']: item['title']['en'] for item in schemas['codelist-licenseStatus']['licenseStatus']}
    listtype_score = {item['code']: item['quality_score'] for item in schemas['codelist-listType']['listType']}
    listtype_names = {item['code']: item['title']['en'] for item in schemas['codelist-listType']['listType']}

    

    for prefix in org_id_lists:
        quality = 0
        quality_explained = {}
        for item in (prefix.get('data', {}).get('availability') or []):
            value = availabilty_score.get(item)
            if value:
                quality += value
                quality_explained["Availability: " + availabilty_names[item]] = value
            else:
                print('No availiablity type {}. Found in code {}'.format(item, prefix['code']))

        if prefix['data'].get('licenseStatus'):
            quality += license_score[prefix['data']['licenseStatus']]
            quality_explained["License: " + license_names[prefix['data']['licenseStatus']]] = license_score[prefix['data']['licenseStatus']]

        if prefix.get('listType'):
            value = listtype_score.get(prefix['listType'])
            if value:
                quality += value
                quality_explained["List type: "  + listtype_names[prefix['listType']]] = value
            else:
                print('No licenseStatus for {}. Found in code {}'.format(prefix['listType'], prefix['code']))

        
        prefix['quality_explained'] = quality_explained
        prefix['quality'] = min(quality, 100)


def augment_structure(org_id_lists):
    for prefix in org_id_lists:
        if not prefix.get('structure'):
            continue
        for structure in prefix['structure']:
            split = structure.split("/")
            if split[0] not in prefix['structure']:
                prefix['structure'].append(split[0])


def add_titles(org_list):
    '''Add coverage_titles and subnationalCoverage_titles to organisation lists'''
    coverage_codes = org_list.get('coverage')
    if coverage_codes:
        org_list['coverage_titles'] = [tup[1] for tup in lookups['coverage'] if tup[0] in coverage_codes]
    subnational_codes = org_list.get('subnationalCoverage')
    if subnational_codes:
        subnational_coverage = []
        for country in coverage_codes:
            subnational_coverage.extend(lookups['subnational'][country])
        org_list['subnationalCoverage_titles'] = [tup[1] for tup in subnational_coverage if tup[0] in subnational_codes]

    structure_codes = org_list.get('structure')
    if structure_codes:
        org_list['structure_titles'] = [tup[1] for tup in lookups['structure'] if tup[0] in structure_codes]

    sector_codes = org_list.get('sector')
    if sector_codes:
        org_list['sector_titles'] = [tup[1] for tup in lookups['sector'] if tup[0] in sector_codes]


def refresh_data():
    global lookups
    global org_id_dict
    global git_commit_ref

    try:
        sha = requests.get(
            'https://api.github.com/repos/opendataservices/org-ids/branches/master'
        ).json()['commit']['sha']
        using_github = True
        if sha == git_commit_ref:
            return "Not updating as sha has not changed: {}".format(sha)
    except Exception:
        using_github = False

    if settings.LOCAL_DATA:
        using_github = False

    if using_github:
        try:
            schemas = load_schemas_from_github()
        except Exception:
            raise
            using_github = False
            schemas = load_schemas_from_disk()
    else:
        schemas = load_schemas_from_disk()

    lookups = create_codelist_lookups(schemas)
    
    if using_github:
        try:
            org_id_lists = load_org_id_lists_from_github()
        except:
            raise
            using_github = False
            org_id_lists = load_org_id_lists_from_disk()
    else:
        org_id_lists = load_org_id_lists_from_disk()

    augment_quality(schemas, org_id_lists)
    augment_structure(org_id_lists)

    org_id_dict = {org_id_list['code']: org_id_list for org_id_list in org_id_lists if org_id_list.get('confirmed')}

    if using_github:
        git_commit_ref = sha
        return "Loaded from github: {}".format(sha)
    else:
        return "Loaded from disk"


refresh_data()


def filter_and_score_results(query):
    indexed = {key: value.copy() for key, value in org_id_dict.items()}
    for prefix in list(indexed.values()):
        prefix['relevance'] = 0
        prefix['relevance_debug'] = []

    coverage = query.get('coverage')
    subnational = query.get('subnational')
    structure = query.get('structure')
    substructure = query.get('substructure')
    sector = query.get('sector')

    for prefix in list(indexed.values()):
        if prefix.get('listType') == 'primary':
            prefix['relevance'] += RELEVANCE["MATCH_DROPDOWN"]
            prefix['relevance_debug'].append("Primary list +" + str(RELEVANCE["MATCH_DROPDOWN_ONLY_VALUE"]))



        if coverage:
            if prefix.get('coverage'):
                if coverage in prefix['coverage']:
                    prefix['relevance'] += RELEVANCE["MATCH_DROPDOWN"]
                    prefix['relevance_debug'].append("Coverage matched: +" + str(RELEVANCE["MATCH_DROPDOWN"]))
                    if len(prefix['coverage']) == 1:
                        prefix['relevance'] += RELEVANCE["MATCH_DROPDOWN_ONLY_VALUE"]
                        prefix['relevance_debug'].append("List only covers this country +" + str(RELEVANCE["MATCH_DROPDOWN_ONLY_VALUE"]))
                    if not subnational and not prefix['subnationalCoverage']:
                        prefix['relevance'] += RELEVANCE["MATCH_DROPDOWN"]/2
                        prefix['relevance_debug'].append("List is only national +" + str(RELEVANCE["MATCH_DROPDOWN"]/2))
                else:
                    indexed.pop(prefix['code'], None)
        else:
            if not prefix.get('coverage'):
                prefix['relevance'] += RELEVANCE["MATCH_EMPTY"]
                prefix['relevance_debug'].append("No coverage value +" + str(RELEVANCE["MATCH_DROPDOWN"]))

        if subnational:
            if prefix.get('subnationalCoverage') and subnational in prefix['subnationalCoverage']:
                prefix['relevance'] += RELEVANCE["MATCH_DROPDOWN"] * 2
                prefix['relevance_debug'].append("Subnational coverage matched +" + str(RELEVANCE["MATCH_DROPDOWN"]*2))
                if len(prefix['subnationalCoverage']) == 1:
                    prefix['relevance'] += RELEVANCE["MATCH_DROPDOWN_ONLY_VALUE"]
                    prefix['relevance_debug'].append("List only covers this subnational area +" + str(RELEVANCE["MATCH_DROPDOWN_ONLY_VALUE"]))
            else:
                indexed.pop(prefix['code'], None)

        if structure:
            if prefix.get('structure'):
                if structure in prefix['structure']:
                    prefix['relevance'] += RELEVANCE["MATCH_DROPDOWN"]
                    prefix['relevance_debug'].append("Structure matched +" + str(RELEVANCE["MATCH_DROPDOWN"]))
                    if len(prefix['structure']) == 1:
                        prefix['relevance'] += RELEVANCE["MATCH_DROPDOWN_ONLY_VALUE"]
                        prefix['relevance_debug'].append("List only covers this structure +" + str(RELEVANCE["MATCH_DROPDOWN_ONLY_VALUE"]))
                else:
                    indexed.pop(prefix['code'], None)
        else:
            if not prefix.get('structure'):
                prefix['relevance'] += RELEVANCE["MATCH_EMPTY"]
                prefix['relevance_debug'].append("No structure value +" + str(RELEVANCE["MATCH_EMPTY"]))

        if substructure:
            if prefix.get('structure') and substructure in prefix['structure']:
                    prefix['relevance'] += RELEVANCE["MATCH_DROPDOWN"] * 2
                    prefix['relevance_debug'].append("Sub-structure matched +" + str(RELEVANCE["MATCH_DROPDOWN"]*2))
            else:
                indexed.pop(prefix['code'], None)

        if sector:
            if prefix.get('sector'):
                if sector in prefix['sector']:
                    prefix['relevance'] += RELEVANCE["MATCH_DROPDOWN"]*2
                    prefix['relevance_debug'].append("Sector matched +" + str(RELEVANCE["MATCH_DROPDOWN"]*2))
                    if len(prefix['sector']) == 1:
                        prefix['relevance'] += RELEVANCE["MATCH_DROPDOWN_ONLY_VALUE"]*2
                        prefix['relevance_debug'].append("List only covers this sector +" + str(RELEVANCE["MATCH_DROPDOWN_ONLY_VALUE"]*2))
                else:
                    indexed.pop(prefix['code'], None)
        else:
            if not prefix.get('sector'):
                prefix['relevance'] += RELEVANCE["MATCH_EMPTY"]
                prefix['relevance_debug'].append("Sector empty +" + str(RELEVANCE["MATCH_EMPTY"]))

    all_results = {"suggested": [],
                   "recommended": [],
                   "other": []}

    if not indexed:
        return all_results

    for num, value in enumerate(sorted(indexed.values(), key=lambda k: -(k['relevance'] * 100 + k['quality']))):
        add_titles(value)
        
        if (value['relevance'] >= RELEVANCE["SUGGESTED_RELEVANCE_THRESHOLD"]
            and value['quality'] > RELEVANCE["SUGGESTED_QUALITY_THRESHOLD"]
            and not all_results['suggested'] or (all_results['suggested'] and value['relevance'] == all_results['suggested'][0]['relevance'])):
            all_results['suggested'].append(value)
        elif value['relevance'] >= RELEVANCE["RECOMENDED_RELEVANCE_THRESHOLD"]:
            all_results['recommended'].append(value)
        else:
            all_results['other'].append(value)

    return all_results


def get_lookups(query_dict):
    ''' Get only those lookup combinations returning some result'''
    valid_lookups = {
        'coverage': None,
        'structure': None,
        'sector': None,
        'subnational': None,
        'substructure': None
    }

    # Needed for subcategories
    coverage = query_dict.get('coverage')
    structure = query_dict.get('structure')
    subnational_lookups = []
    substructure_lookups = []

    queries = []
    fields = ('coverage', 'structure', 'sector', 'subnational', 'substructure')

    # Build queries, one per search dropdown
    for field in fields:
        if field == 'subnational' or field == 'substructure':
            single_query = {'lookups': field}
        else:
            single_query = {'lookups': (field, [[], False])}

        for key, value in query_dict.items():
            if key == field:
                single_query[field] = ''
            else:
                single_query[key] = value
        queries.append(single_query)

    # Run the queries popping those lists that won't be returned
    # from a dict (list_code:list_data) of id lists.
    for q in queries:
        indexed = {key: value for key, value in org_id_dict.items()}
        for org_list in list(indexed.values()):

            for key, value in q.items():
                if key == 'lookups':
                    continue
                if value:
                    if key == 'subnational' or key == 'substructure':
                        key = 'subnationalCoverage' if key == 'subnational' else 'structure'
                        if org_list.get(key) and value not in org_list[key] or not org_list.get(key):
                            indexed.pop(org_list['code'], None)
                    else:
                        if org_list.get(key) and value not in org_list[key]:
                            indexed.pop(org_list['code'], None)

        if isinstance(q['lookups'], tuple):
            field, field_lookup = q['lookups']
            for result in indexed.values():
                if result.get(field):
                    field_lookup[0].extend([item for item in result[field]])
                else:
                    field_lookup[1] = True
                    break
            else:
                field_lookup[0] = set(field_lookup[0])

        elif q['lookups'] == 'subnational' and coverage:
            for result in indexed.values():
                if result.get('subnationalCoverage'):
                    subnational_lookups.extend([region for region in result['subnationalCoverage']])
            subnational_lookups = set(subnational_lookups)
        elif q['lookups'] == 'substructure' and structure:
            for result in indexed.values():
                if result.get('structure'):
                    substructure_lookups.extend([structure for structure in result['structure']])
            substructure_lookups = set(substructure_lookups)

    # Filter valid lookups out of all (global) lookups
    for q in queries:
        if isinstance(q['lookups'], tuple):
            field, field_lookup = q['lookups']
            if field_lookup[1]:
                valid_lookups[field] = lookups[field]
            else:
                valid_lookups[field] = [tup + (False, ) if tup[0] in field_lookup[0] else tup + (True, ) for tup in lookups[field]]

    if lookups['subnational'].get(coverage):
        if subnational_lookups:
            valid_lookups['subnational'] = [
                tup + (False, ) if tup[0] in subnational_lookups else tup + (True, )
                for tup in lookups['subnational'][coverage]
            ]
        else:
            valid_lookups['subnational'] = [tup + (True, ) for tup in lookups['subnational'][coverage]]
    else:
        valid_lookups['subnational'] = []

    if lookups['substructure'].get(structure):
        if substructure_lookups:
            valid_lookups['substructure'] = [
                tup + (False,) if tup[0] in substructure_lookups else tup + (True, )
                for tup in lookups['substructure'][structure]
            ]
        else:
            valid_lookups['substructure'] = [tup + (True, ) for tup in lookups['substructure'][structure]]
    else:
        valid_lookups['substructure'] = []

    return valid_lookups


def update_lists(request):
    return HttpResponse(refresh_data())


def home(request):
    query = {key: value for key, value in request.GET.items() if value}
    context = {
        "lookups": {
            'coverage': lookups['coverage'],
            'structure': lookups['structure'],
            'sector': lookups['sector']
        }
    }
    if query:
        context['lookups'] = get_lookups(query)
        context['all_results'] = filter_and_score_results(query)
        context['query'] = query
    else:
        query = {'coverage': '', 'structure': '', 'sector': ''}
        context['query'] = False
        context['all_results'] = {}


    context['local'] = settings.LOCAL_DATA
    

    return render(request, "home.html", context=context)


def list_details(request, prefix):
    try:
        org_list = org_id_dict[prefix].copy()
        add_titles(org_list)

    except KeyError:
        raise Http404('Organisation list {} does not exist'.format(prefix))
    return render(request, 'list.html', context={'org_list': org_list})


def _get_filename():
    if git_commit_ref:
        return git_commit_ref[:10]
    else:
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def json_download(request):
    response = HttpResponse(json.dumps({"lists": list(org_id_dict.values())}, indent=2), content_type='text/json')
    response['Content-Disposition'] = 'attachment; filename="org-id-{0}.json"'.format(_get_filename())
    return response


def _flatten_list(obj, path=''):
    # probably use flattentool but only when schema data validates
    for key, value in obj.items():
        if isinstance(value, dict):
            yield from _flatten_list(value, path + "/" + key)
        elif isinstance(value, list):
            yield (path + "/" + key).lstrip("/"), ", ".join(value)
        else:
            yield (path + "/" + key).lstrip("/"), value


def csv_download(request):
    all_keys = set()
    all_rows = []
    for item in org_id_dict.values():
        row = dict(_flatten_list(item))
        all_keys.update(row.keys())
        all_rows.append(row)

    all_keys.remove("code")
    all_keys.remove("description/en")

    headers = ["code", "description/en"] + sorted(list(all_keys))

    output = io.StringIO()

    writer = csv.DictWriter(output, headers)
    writer.writeheader()
    writer.writerows(all_rows)

    response = HttpResponse(output.getvalue(), content_type='text/csv')

    response['Content-Disposition'] = 'attachment; filename="org-id-{0}.csv"'.format(_get_filename())
    return response


import lxml.etree as ET


def make_xml_codelist():
    root = ET.Element("codelist")
    meta = ET.SubElement(root, "metadata")
    ET.SubElement(ET.SubElement(meta, "name"),"narrative").text = "Organization Identifier Lists"
    ET.SubElement(ET.SubElement(meta, "description"),"narrative").text = "Organisation identifier lists and their code. These can be used as the prefix for an organisation identifier. For general guidance about constructing Organisation Identifiers, please see http://iatistandard.org/organisation-identifiers/  This list was formerly maintained by the IATI Secretariat as the Organization Registration Agency codelist. This version is maintained by the Identify-Org project, of which IATI is a member. New code requests should be made via Identify-org.net"
    items = ET.SubElement(root, "codelist-items")

    for entry in org_id_dict.values():
        if entry['access'] and entry['access']['availableOnline']:
            publicdb = str(1)
        else:
            publicdb = str(0)
    
        item = ET.SubElement(items, "codelist-item",**{'public-database':publicdb})
        ET.SubElement(item, "code").text = entry['code']

        name = ET.SubElement(item, "name")
        ET.SubElement(name, "narrative").text = entry['name']['en']

        description = ET.SubElement(item, "description")
        ET.SubElement(description, "narrative").text = entry['description']['en']
        if entry['coverage']:
            ET.SubElement(item, "category").text = entry['coverage'][0]
        else:
            ET.SubElement(item, "category").text = '-'
        ET.SubElement(item, "url").text = entry['url']
        
    return ET.tostring(root, encoding='unicode', pretty_print=True)


def xml_download(request):
    response = HttpResponse(make_xml_codelist(), content_type='text/xml')
    response['Content-Disposition'] = 'attachment; filename="org-id-{0}.xml"'.format(_get_filename())
    return response
