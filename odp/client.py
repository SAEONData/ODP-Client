from typing import List, Dict, Any, Optional

import requests
from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.requests_client import OAuth2Session

from .config import Config
from .exceptions import ODPException, ODPAuthError, ODPServerError, ODPClientError

__all__ = ['ODPClient']


class ODPClient:
    """ Provides programmatic access to the SAEON Open Data Platform API,
    authorized by a client credentials grant.

    Configuration is read from the environment. The following options are
    supported::

        ODP_PUBLIC_API - URL of the ODP Public API
        ODP_ADMIN_API - URL of the ODP Admin API (optional; requires internal network access)
        OAUTH2_SERVER - URL of the Hydra OAuth2 server
        OAUTH2_CLIENT_ID - registered client ID
        OAUTH2_CLIENT_SECRET - registered client secret
        OAUTH2_SCOPE - whitespace-delimited list of scopes
    """

    def __init__(self, timeout: Optional[float] = 5.0):
        self.public_url = Config.ODP_PUBLIC_API
        self.admin_url = Config.ODP_ADMIN_API
        self.auth_url = Config.OAUTH2_SERVER
        self.client_id = Config.OAUTH2_CLIENT_ID
        self.client_secret = Config.OAUTH2_CLIENT_SECRET
        self.scope = Config.OAUTH2_SCOPE
        self.timeout = timeout
        self.client_session = OAuth2Session(
            self.client_id,
            self.client_secret,
            scope=self.scope,
        )
        self._token = None

    @property
    def token(self):
        if self._token is None:
            try:
                self._token = self.client_session.fetch_token(
                    self.auth_url + '/oauth2/token',
                    grant_type='client_credentials',
                    timeout=self.timeout,
                )
            except OAuthError as e:
                raise ODPAuthError(*e.args) from e
            except requests.RequestException as e:
                raise ODPServerError(*e.args, status_code=503) from e

        return self._token

    def _request(self, url, method, endpoint, json=None):
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.token['access_token'],
        }
        if method in ('POST', 'PUT'):
            headers['Content-Type'] = 'application/json'

        try:
            r = requests.request(
                method, url + endpoint,
                json=json,
                headers=headers,
                timeout=self.timeout,
            )
            r.raise_for_status()
            return r.json()

        except requests.HTTPError as e:
            if (status_code := e.response.status_code) == 403:
                exc = ODPAuthError
            elif 400 <= status_code < 500:
                exc = ODPClientError
            elif 500 <= status_code < 600:
                exc = ODPServerError
            else:
                exc = ODPException

            try:
                error_detail = e.response.json()
            except ValueError:
                error_detail = e.response.text

            raise exc(*e.args, status_code=status_code, error_detail=error_detail) from e

        except requests.RequestException as e:
            raise ODPServerError(*e.args, status_code=503) from e

    def list_institutions(self) -> List[Dict[str, Any]]:
        return self._request(
            url=self.admin_url,
            method='GET',
            endpoint='/institution/',
        )

    def list_metadata_records(
            self,
            institution_key: str,
            offset: int = 0,
            limit: int = 100,
    ) -> List[Dict[str, Any]]:
        return self._request(
            url=self.public_url,
            method='GET',
            endpoint=f'/{institution_key}/metadata/?offset={offset}&limit={limit}',
        )

    def get_metadata_record(
            self,
            institution_key: str,
            record_id: str,
    ) -> Dict[str, Any]:
        return self._request(
            url=self.public_url,
            method='GET',
            endpoint=f'/{institution_key}/metadata/{record_id}',
        )

    def create_or_update_metadata_record(
            self,
            institution_key: str,
            collection_key: str,
            schema_key: str,
            metadata: Dict[str, Any],
            terms_conditions_accepted: bool,
            data_agreement_accepted: bool,
            data_agreement_url: str,
            capture_method: str,
            doi: str = '',
            auto_assign_doi: bool = False,
    ) -> Dict[str, Any]:
        return self._request(
            url=self.public_url,
            method='POST',
            endpoint=f'/{institution_key}/metadata/',
            json={
                'collection_key': collection_key,
                'schema_key': schema_key,
                'metadata': metadata,
                'terms_conditions_accepted': terms_conditions_accepted,
                'data_agreement_accepted': data_agreement_accepted,
                'data_agreement_url': data_agreement_url,
                'capture_method': capture_method,
                'doi': doi,
                'auto_assign_doi': auto_assign_doi,
            }
        )
