from .views import make_xml_codelist
import requests
import io
from lxml import etree
import os



def test_xml_codelists():
    schema = open(os.path.dirname(os.path.realpath(__file__)) + "/codelist.xsd").read()
    schema_file = io.StringIO(schema)
    schema_file_parsed = etree.parse(schema_file)

    xmlschema = etree.XMLSchema(schema_file_parsed)
    created_xml_codelist = make_xml_codelist('main')
    created_xml_codelist_file = io.StringIO(created_xml_codelist)
    xml_codelist_etree = etree.parse(created_xml_codelist_file)

    xmlschema.assertValid(xml_codelist_etree)
