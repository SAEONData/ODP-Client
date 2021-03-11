# ODP Client

A Python client for the SAEON Open Data Platform API.

## Requirements

Requires Python 3.8 or above.

An OAuth2 client credentials grant is required for your application to access the ODP.

## Usage

See `example.py` for example usage.

### Environment variables

The library reads the following environment variables.

- `ODP_PUBLIC_API`: URL of the ODP Public API
- `ODP_ADMIN_API`: URL of the ODP Admin API (optional; requires internal network access)
- `OAUTH2_SERVER`: URL of the Hydra OAuth2 server
- `OAUTH2_CLIENT_ID`: registered client ID for your application
- `OAUTH2_CLIENT_SECRET`: registered client secret for your application
- `OAUTH2_SCOPE`: whitespace-delimited list of scopes required by your application

_N.B. Don't commit secrets to source control. If you load environment variables from
a `.env` file, be sure to add a `.gitignore` rule for `.env` to your project._

### ODP server certificate verification

For admin API usage, or if using this client in a non-production environment,
you will need to install the applicable SAEON CA certificate to your system,
and tell the `requests` module to use your system certificates.

The CA certificate may be downloaded from `https://odp-admin.saeon.xyz/ca.crt`
(replace `.xyz` with the applicable domain suffix).

Debian/Ubuntu:

    sudo cp ca.crt /usr/local/share/ca-certificates/
    sudo update-ca-certificates
    export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

CentOS/Fedora:

    sudo cp ca.crt /etc/pki/ca-trust/source/anchors/
    sudo update-ca-trust
    export REQUESTS_CA_BUNDLE=/etc/pki/tls/cert.pem
