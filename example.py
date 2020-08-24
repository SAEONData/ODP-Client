from pprint import pprint

from dotenv import load_dotenv

from odp.client import ODPClient
from odp.exceptions import ODPException

load_dotenv()

client = ODPClient()
try:
    result = client.list_metadata_records('saeon')
    pprint(result, indent=4)
except ODPException as e:
    print(f"{e}: {e.error_detail}")
