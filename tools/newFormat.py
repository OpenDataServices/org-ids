import os
import json
import glob

struct_map = {}
with open('../schema/codelist-structure.json','r') as structure_file:
    structures = json.loads(structure_file.read())
    for structure in structures['structure']:
        struct_map[structure['code'].split("/").pop()] = structure['code']

def create_tag(title):
    if(title):
        return str(title.replace(" / ","_").replace("  "," ").replace(" ","_").lower())
    else:
        return None

codes_dir = "../codes/"

for prefix_file_name in glob.glob(codes_dir + '/*/*.json'):
    print(prefix_file_name)
    with open(prefix_file_name,"r") as prefix_file:
        old = json.loads(prefix_file.read())
        new = {
            "name":{
                "en":old['name'].split("/")[0],
                "local":(old['name'] + "/").split("/")[1]
            },
            "description":{
                "en":old['description']
            },
            "code":old['code'],
            "url":old['url'],
            "registerType":create_tag(old['registerType']),
            "jurisdiction":[list(map(lambda x: x['countryCode'],old['jurisdiction'])) if old['jurisdiction'] else None],
            "subnationalJurisdiction":[list(map(lambda x: x['regionCode'],old['subnational'])) if old['subnational'] else None],
            "sector":list(map(lambda x: create_tag(x['name']),old['sector'])) if old['sector'] else None,
            "structure":list(map(lambda x: struct_map[create_tag(x['name'])],old['structure'])) if old['structure'] else None,
            "access": {
                "availableOnline": True if (old['availableOnline']) == "yes" else False,
                "onlineAccessDetails": old['onlineAccessDetails'],
                "publicDatabase": old['publicDatabase'],
                "guidanceOnLocatingIds": old['guidanceOnLocatingIds'],
                "exampleIdentifiers": old['exampleIdentifiers'],
                "languages": old['languages']
            },
            "data": {
                "availability": list(map(lambda x: create_tag(x),old['dataAccessProperties'])) if old['dataAccessProperties'] else None,
                "dataAccessDetails": old['dataAccessDetails'],
                "features": list(map(lambda x: create_tag(x),old['datasetFeatures'])) if old['datasetFeatures'] else None,
                "licenseStatus": create_tag(old['licenseStatus']),
                "licenseDetails": old['licenseDetails']
            },
            "meta": {
                "source": old['source'],
                "lastUpdated": old['lastUpdated']
            },
            "links":{
                "opencorporates": "http://opencorporates.com/companies/" + old['jurisdiction'][0]['countryCode'].lower() if old['opencorporates'] else None ,
                "wikipedia":old['wikipedia']
            },
            "confirmed":old['confirmed'],
            "deprecated":old['deprecated'],
            "formerPrefixes":old['former_prefixes']

        }

    with open(prefix_file_name,"w") as prefix_write:
        prefix_write.write(json.dumps(new, indent=4))

