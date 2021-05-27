import os
from typing import List, Dict, Any, Optional, Iterable

import requests
from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.requests_client import OAuth2Session

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

    def __init__(
            self,
            *,
            verify: bool = True,
            timeout: Optional[float] = 5.0,
    ):
        """ Constructor. The optional parameters should typically only be used
        when connecting to local dev instances of the API and auth servers.
        """
        self.public_url = os.environ['ODP_PUBLIC_API']
        self.admin_url = os.getenv('ODP_ADMIN_API')
        self.auth_url = os.environ['OAUTH2_SERVER']
        self.client_id = os.environ['OAUTH2_CLIENT_ID']
        self.client_secret = os.environ['OAUTH2_CLIENT_SECRET']
        self.scope = os.environ['OAUTH2_SCOPE']
        self.verify = verify
        self.timeout = timeout
        self.client_session = OAuth2Session(
            self.client_id,
            self.client_secret,
            scope=self.scope,
        )
        self._token = None

    # region Institution API (admin)

    def list_institutions(self) -> List[Dict[str, Any]]:
        return self._request(
            admin_api=True,
            method='GET',
            endpoint='/institution/',
        )

    def get_institution(
            self,
            key: str,
    ) -> Dict[str, Any]:
        return self._request(
            admin_api=True,
            method='GET',
            endpoint=f'/institution/{key}',
        )

    def create_or_update_institution(
            self,
            key: str,
            name: str,
            parent_key: Optional[str],
            domain_names: Iterable[str],
    ) -> Dict[str, Any]:
        return self._request(
            admin_api=True,
            method='POST',
            endpoint='/institution/',
            json={
                'key': key,
                'name': name,
                'parent_key': parent_key,
                'domain_names': domain_names,
            }
        )

    # endregion

    # region Collection API

    def list_metadata_collections(
            self,
            institution_key: str,
    ) -> List[Dict[str, Any]]:
        return self._request(
            method='GET',
            endpoint=f'/{institution_key}/collection/',
        )

    def create_or_update_metadata_collection(
            self,
            institution_key: str,
            key: str,
            name: str,
            *,
            description: str = None,
            doi_scope: str = None,
            project_keys: Iterable[str] = (),
    ) -> Dict[str, Any]:
        return self._request(
            method='POST',
            endpoint=f'/{institution_key}/collection/',
            json={
                'key': key,
                'name': name,
                'description': description,
                'doi_scope': doi_scope,
                'project_keys': project_keys,
            }
        )

    # endregion

    # region Metadata API

    def list_metadata_records(
            self,
            institution_key: str,
            *,
            offset: int = 0,
            limit: int = 100,
    ) -> List[Dict[str, Any]]:
        return self._request(
            method='GET',
            endpoint=f'/{institution_key}/metadata/',
            params={
                'offset': offset,
                'limit': limit,
            }
        )

    def get_metadata_record(
            self,
            institution_key: str,
            *,
            record_id: str = None,
            doi: str = None,
            sid: str = None,
    ) -> Dict[str, Any]:
        if record_id:
            return self._request(
                method='GET',
                endpoint=f'/{institution_key}/metadata/{record_id}',
            )
        elif doi:
            return self._request(
                method='GET',
                endpoint=f'/{institution_key}/metadata/doi/{doi}',
            )
        elif sid:
            return self._request(
                method='GET',
                endpoint=f'/{institution_key}/metadata/sid/{sid}',
            )

    def create_or_update_metadata_record(
            self,
            institution_key: str,
            collection_key: str,
            schema_key: str,
            metadata: Dict[str, Any],
            *,
            doi: str = None,
            sid: str = None,
    ) -> Dict[str, Any]:
        return self._request(
            method='POST',
            endpoint=f'/{institution_key}/metadata/',
            json={
                'collection_key': collection_key,
                'schema_key': schema_key,
                'metadata': metadata,
                'doi': doi,
                'sid': sid,
            }
        )

    def validate_metadata_record(
            self,
            institution_key: str,
            record_id: str,
    ) -> Dict[str, Any]:
        """ Validate a metadata record.
        :return: {"success": bool, "errors": dict}
        """
        return self._request(
            method='POST',
            endpoint=f'/{institution_key}/metadata/validate/{record_id}',
        )

    def change_state_of_metadata_record(
            self,
            institution_key: str,
            record_id: str,
            state: str,
    ) -> Dict[str, Any]:
        """ Set the workflow state of a metadata record.
        :return: {"success": bool, "errors": dict}
        """
        return self._request(
            method='POST',
            endpoint=f'/{institution_key}/metadata/workflow/{record_id}',
            params={'state': state},
        )

    # endregion

    # region Project API (admin)

    def list_projects(self) -> List[Dict[str, Any]]:
        return self._request(
            admin_api=True,
            method='GET',
            endpoint='/project/',
        )

    def create_or_update_project(
            self,
            key: str,
            abbr: str,
            name: str,
    ) -> Dict[str, Any]:
        return self._request(
            admin_api=True,
            method='POST',
            endpoint='/project/',
            json={
                'key': key,
                'abbr': abbr,
                'name': name,
            }
        )

    # endregion

    # region Schema API (admin)

    def list_schemas(self) -> List[Dict[str, Any]]:
        return self._request(
            admin_api=True,
            method='GET',
            endpoint='/schema/',
        )

    def create_or_update_schema(
            self,
            key: str,
            name: str,
            schema: Dict[str, Any],
            *,
            template: Dict[str, Any] = None,
            attr_mappings: Dict[str, str] = None
    ) -> Dict[str, Any]:
        return self._request(
            admin_api=True,
            method='POST',
            endpoint='/schema/',
            json={
                'key': key,
                'name': name,
                'schema': schema,
                'template': template or {},
                'attr_mappings': attr_mappings or {},
            }
        )

    # endregion

    # region Workflow API (admin)
    
    def list_workflow_states(self) -> List[Dict[str, Any]]:
        return self._request(
            admin_api=True,
            method='GET',
            endpoint='/workflow/state/',
        )

    def create_or_update_workflow_state(
            self,
            key: str,
            name: str,
            rules: Dict[str, Any],
            revert_key: Optional[str],
            publish: bool,
    ) -> Dict[str, Any]:
        return self._request(
            admin_api=True,
            method='POST',
            endpoint='/workflow/state/',
            json={
                'key': key,
                'name': name,
                'rules': rules,
                'revert_key': revert_key,
                'publish': publish,
            }
        )

    def list_workflow_transitions(self) -> List[Dict[str, Any]]:
        return self._request(
            admin_api=True,
            method='GET',
            endpoint='/workflow/transition/',
        )

    def create_or_update_workflow_transition(
            self,
            from_key: Optional[str],
            to_key: str,
    ) -> Dict[str, Any]:
        return self._request(
            admin_api=True,
            method='POST',
            endpoint='/workflow/transition/',
            json={
                'from_key': from_key,
                'to_key': to_key,
            }
        )

    def list_workflow_annotations(self) -> List[Dict[str, Any]]:
        return self._request(
            admin_api=True,
            method='GET',
            endpoint='/workflow/annotation/',
        )

    def create_or_update_workflow_annotation(
            self,
            key: str,
            attributes: Dict[str, Any],
    ) -> Dict[str, Any]:
        return self._request(
            admin_api=True,
            method='POST',
            endpoint='/workflow/annotation/',
            json={
                'key': key,
                'attributes': attributes,
            }
        )

    # endregion

    # region Catalogue API

    def list_catalogue_records(
            self,
            *,
            institution_key: str = None,
            include_unpublished: bool = False,
            offset: int = 0,
            limit: int = 100,
    ) -> List[Dict[str, Any]]:
        return self._request(
            method='GET',
            endpoint=f'/catalogue/',
            params={
                'institution_key': institution_key,
                'include_unpublished': include_unpublished,
                'offset': offset,
                'limit': limit,
            }
        )

    def count_catalogue_records(
            self,
            *,
            institution_key: str = None,
            include_unpublished: bool = False,
    ) -> int:
        return self._request(
            method='GET',
            endpoint=f'/catalogue/count',
            params={
                'institution_key': institution_key,
                'include_unpublished': include_unpublished,
            }
        )

    def get_catalogue_record(
            self,
            record_id: str,
    ) -> Dict[str, Any]:
        return self._request(
            method='GET',
            endpoint=f'/catalogue/{record_id}',
        )

    def select_catalogue_records(
            self,
            *record_ids: str,
            offset: int = 0,
            limit: int = 100,
    ) -> List[Dict[str, Any]]:
        return self._request(
            method='POST',
            endpoint=f'/catalogue/',
            json=list(record_ids),
            params={
                'offset': offset,
                'limit': limit,
            }
        )

    # endregion

    # region DataCite API (admin)

    def list_datacite_dois(
            self,
            *,
            page_size: int = 100,
            page_num: int = 1,
    ) -> Dict[str, Any]:
        return self._request(
            admin_api=True,
            method='GET',
            endpoint='/datacite/',
            params={
                'page_size': page_size,
                'page_num': page_num,
            }
        )

    def get_datacite_doi(
            self,
            doi: str,
    ) -> Dict[str, Any]:
        return self._request(
            admin_api=True,
            method='GET',
            endpoint=f'/datacite/{doi}',
        )

    # endregion

    def _request(self, method, endpoint, *, admin_api=False, params=None, json=None):
        if admin_api:
            if not (server_url := self.admin_url):
                raise ODPException("ODP Admin API URL is required")
        else:
            server_url = self.public_url

        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.token['access_token'],
        }
        if method in ('POST', 'PUT'):
            headers['Content-Type'] = 'application/json'

        try:
            r = requests.request(
                method, server_url + endpoint,
                params=params,
                json=json,
                headers=headers,
                verify=self.verify,
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

    @property
    def token(self):
        if self._token is None:
            try:
                self._token = self.client_session.fetch_token(
                    self.auth_url + '/oauth2/token',
                    grant_type='client_credentials',
                    verify=self.verify,
                    timeout=self.timeout,
                )
            except OAuthError as e:
                raise ODPAuthError(*e.args, status_code=403) from e
            except requests.RequestException as e:
                raise ODPServerError(*e.args, status_code=503) from e

        return self._token
