"""
openEHR Definitions Kubernetes Operator

Listens to ConfigMaps with the label 'openehr.org/definitiontype' set to a
valid DefinitionType and then attempts to create or update them using the
openEHR Definition API residing at the configured base URL.
"""

import os
import kopf
import yaml
import requests

from enum import StrEnum
from urllib.parse import urljoin

# Global settings taken from Environment variables
OPENEHR_API_BASEURL = os.environ.get('OPENEHR_API_BASEURL')
MAX_RETRIES = os.environ.get('MAX_RETRIES', None)
FAILURE_BACKOFF = os.environ.get('FAILURE_BACKOFF', 60)


### Global paths and variables ###

DEFINITION_TYPE_LABEL = "openehr.org/definitiontype"

class DefinitionType(StrEnum):
    TEMPLATE_ADL1_4 = "template-adl1.4"
    TEMPLATE_ADL2 = "template-adl2"
    QUERY = "query"

PATH = {}
PATH[DefinitionType.TEMPLATE_ADL1_4] = "definition/template/adl1.4"
PATH[DefinitionType.TEMPLATE_ADL2] = "definition/template/adl2"
PATH[DefinitionType.QUERY] = "definition/query"

HEADERS = {}
HEADERS[DefinitionType.TEMPLATE_ADL1_4] = {'Content-type': 'application/xml', 'Prefer': 'return=minimal'}
HEADERS[DefinitionType.TEMPLATE_ADL2] = {'Content-type': 'text/plain', 'Prefer': 'return=minimal'}
HEADERS[DefinitionType.QUERY] = {'Content-type': 'text/plain'}


### Startup Checks and Configuration ###

@kopf.on.startup()
def startup(settings: kopf.OperatorSettings, **_):
    if OPENEHR_API_BASEURL is None:
        raise kopf.PermanentError("Missing required environment variable OPENEHR_API_BASEURL.")


### Main logic functions ###

def post_definitions(definitiontype: DefinitionType, data: dict):
    url = urljoin(OPENEHR_API_BASEURL, PATH[definitiontype])
    headers = HEADERS[definitiontype]

    match definitiontype:
        case DefinitionType.TEMPLATE_ADL1_4 | DefinitionType.TEMPLATE_ADL2:
            print(f"Creating new ADL templates against the path {url}")
            for key, value in data.items():
                print(f"Creating template from data key '{key}'")
                response = requests.post(url=url, data=value, headers=headers)
                print(f"Response code was {response.status_code}, body was:\n{response.text}")
                if not response.ok:
                    return False
        case _:
            raise kopf.PermanentError(f"Unsupported definitiontype '{definitiontype}'")
            return False

    return True


### Resource Event Handlers ###
# can use several different parameters as needed, see: https://kopf.readthedocs.io/en/stable/kwargs/#resource-related-kwargs 

@kopf.on.create('configmap', labels={DEFINITION_TYPE_LABEL: kopf.PRESENT}, retries=MAX_RETRIES, backoff=FAILURE_BACKOFF)
def create(body, labels, retry, **_):
    definitiontype = DefinitionType(labels[DEFINITION_TYPE_LABEL].lower())
    if not post_definitions(definitiontype, body['data']):
        raise kopf.TemporaryError(f"Failure creating definitions? TODO")
    
    return "Created successfully."

@kopf.on.update('configmap',
                labels={DEFINITION_TYPE_LABEL: kopf.PRESENT},
                field='data',
                new=kopf.PRESENT,
                retries=MAX_RETRIES,
                backoff=FAILURE_BACKOFF)
def update(old, new, body, labels, retry, diff, **_):
    # In theory body and new are same -- maybe we don't care about looking at old and new?
    definitiontype = DefinitionType(labels[DEFINITION_TYPE_LABEL].lower())
    if not post_definitions(definitiontype, body['data']):
        raise kopf.TemporaryError(f"Failure updating definitions? TODO")

    return "Updated successfully."

@kopf.on.delete('configmap', labels={DEFINITION_TYPE_LABEL: kopf.PRESENT}, retries=MAX_RETRIES, backoff=FAILURE_BACKOFF)
def delete(body, retry, **_):
    return "Delete not currently supported by the openEHR Definition API. The resources will not be removed."
