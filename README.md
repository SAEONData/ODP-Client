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

_N.B. DO NOT commit secrets to source control. If you load environment variables from
a `.env` file, be sure to add a `.gitignore` rule for `.env` to your project._

### ODP server certificate verification

If using this library in a non-production environment, you will need to install the
SAEON CA certificate on your system, and tell the Python `requests` module to use the
system certificates, by setting the `REQUESTS_CA_BUNDLE` environment variable.
For Debian/Ubuntu, the value should typically be `/etc/ssl/certs/ca-certificates.crt`.
