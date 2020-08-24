import os


class Config:
    ODP_PUBLIC_API = os.environ['ODP_PUBLIC_API']
    ODP_ADMIN_API = os.getenv('ODP_ADMIN_API')
    OAUTH2_SERVER = os.environ['OAUTH2_SERVER']
    OAUTH2_CLIENT_ID = os.environ['OAUTH2_CLIENT_ID']
    OAUTH2_CLIENT_SECRET = os.environ['OAUTH2_CLIENT_SECRET']
    OAUTH2_SCOPE = os.environ['OAUTH2_SCOPE']
