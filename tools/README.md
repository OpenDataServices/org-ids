# Airtable to JSON

This script:

* Fetches complete tables from the AirTable API, taking care of paging through results (```api_call```)
* Builds a dictionary of records, each identified with their internal AirTable record ID (```record_map```)
* Builds an output JSON file based on a mapping and table_map (```build_output```)

The mapping is provided as a dictionary in which the keys are AirTable column names, and the values are the field name required in the output.

This de-couples the need to name AirTable columns the same as output data fields.

Only the columns included in the mapping will be included in the output.

The **table_mapping** is provided as a dictionary in which the key are an AirTable column that is of the 'Link to another table' type. The value is a dictionary with 'data' and 'mapping' keys. Data should provide a dictionary of records from the table the columns links to. Mapping should provide a mapping object to determine the nature of the output that should be produced. 

## Notes

If the AirTable structure changes, the mappings may need to be updated

AirTable rate limits API calls to 5 per second. We use the ratelimit module to manage this. 

s