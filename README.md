# Org-ID: A list of lists

We are creating a simple proces, tool and codelist to enable data publishers and users to create and use joined up data that identifies organisations. 

This involves

* Maintaining an list of organisation identifier lists;
* Developing a methodology for updating the list
* Providing simple lookup tools, and guidance on choosing the best identifiers to use

## The register of organisation identifier lists

An organisation identifier list is any list that contains at least an identifier, and a name, for a collection of organisations. 

Building on the [IATI Organisation Registration Agency codelist](http://iatistandard.org/202/codelists/OrganisationRegistrationAgency/) we are creating an updated register of organisation identifier lists.

This list will contain detailed meta-data on the nature of the identifiers provided, the coverage of identifier lists. It will provide a unique code to identify each list. 

This code can be used as a prefix to create simple identifier strings, or can be used as the 'scheme' in a two-part identifier.

### For example:

The code for the organisation identifier list provided by UK Companies House is 'GB-COH'. The identifier assigned to Open Data Services Co-operative Ltd in this list is '09506232'. Putting this together allows a dataset to unambiguously identify Open Data Services Co-operative Ltd as:

GB-COH-09506232 

or in a table such as:

| Organisation ID Scheme | Organisation ID |
|------------------------|-----------------|
| GB-COH                 | 09506232        |

### Developing the list of lists

We are prototyping our updated register on GitHub: you can find codelists in the ```/codes/``` directory.

These are structured based on the ```list-schema.json``` JSON Schema in the ```/schema/``` directory. 

We have imported codes from a range of sources, and have been updating these [based on the process in our Researchers Handbook](https://docs.google.com/document/d/1lkLjHxXaH9GuAR_g-pv9Qru28f1EeOMZtwXduVboMa4/edit#).

Only those entries with a ```"confirmed":true``` have been reviewed and should be relied upon. All others should be treated as provision.

#### Help us out

Pull requests to update any codes, or suggest new codes are welcome. 


## List Finder Django App

### Installation
Steps to installation:

* Clone the repository
* Change into the cloned repository
* Create a virtual environment (note this application uses python3)
* Activate the virtual environment
* Install dependencies
* Run the development server

```
git clone https://github.com/OpenDataServices/org-ids.git
cd org-ids
virtualenv .ve --python=/usr/bin/python3
source .ve/bin/activate
pip install -r requirements_dev.txt
python manage.py runserver
```


## Tools

### Setup 

The scripts in tools/ have a number of requirements. 

Set-up a virtual environment to easily install these. 

```
virtualenv --python=/usr/local/bin/python3 .ve
source .ve/bin/activate
pip install -r requirements.txt
```
