# org.prefix.codes

We are creating a simple proces, tool and codelist to enable data publishers and users to create and use joined up data that identifies organisations. 

This involves

* Maintaining an register of organisation identifier lists;
* Developing a methodology for updating the list
* Providing simple lookup tools, and guidance on choosing the best identifiers to use

## The register of organisation identifier lists

An organisation identifier list is any list that contains at least an identifier, and a name, for a collection of organisations. 

Building on the [IATI Organisation Registration Agency codelist](http://iatistandard.org/202/codelists/OrganisationRegistrationAgency/) we are creating an updated register of organisation identifier lists.

This register will contain detailed meta-data on the nature of the identifiers provided, the coverage of identifier lists. It will provide a unique code to identify each list. 

This code can be used as a prefix to create simple identifier strings, or can be used as the 'scheme' in a two-part identifier.

### For example:

The code for the organisation identifier list provided by UK Companies House is 'GB-COH'. The identifier assigned to Open Data Services Co-operative Ltd in this list is '09506232'. Putting this together allows a dataset to unambiguously identify Open Data Services Co-operative Ltd as:

GB-COH-09506232 

or in a table such as:

| Organisation ID Scheme | Organisation ID |
|------------------------|-----------------|
| GB-COH                 | 09506232        |

### Developing the register

We are prototyping our updated register using AirTable. Read-only access to the work in progress is [available here](https://airtable.com/shrlr8YfWrz8f9xSf/tblAPFyWmOBCJeiCU/viwUrFgl2nQCTUv4m).

### Data 

The tools/airtable-to-json.py script is used to fetch data from AirTable and to build a set of local json files in the ```data/``` folder. 

## Tools

### Setup 

The scripts in tools/ have a number of requirements. 

Set-up a virtual environment to easily install these. 

```
virtualenv --python=/usr/local/bin/python3 .ve
source .ve/bin/activate
pip install -r requirements.txt
```

### airtable-to-python.py

To run this script you will first need to:

* Have API access to the [Organisation Identifier Lists AirTable](https://airtable.com/shrlr8YfWrz8f9xSf/tblAPFyWmOBCJeiCU/viwUrFgl2nQCTUv4m)
* Set you ```airtable_api_key``` as an environment variable by running ```export airtable_api_key=API_KEY```

Then run:

```
cd tools/
python airtable-to-python.py
```

This should update the files in ```data/``` 
