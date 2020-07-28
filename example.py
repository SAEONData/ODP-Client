from pprint import pprint

from odp.client import ODPClient
from odp.exceptions import ODPException

client = ODPClient(timeout=None)
try:
    result = client.list_metadata_records('saeon')
    pprint(result, indent=4)
except ODPException as e:
    pprint(e)
