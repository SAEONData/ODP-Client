from setuptools import setup, find_packages

version = '1.4.0'

setup(
    name='ODP-Client',
    version=version,
    description='A client for the SAEON Open Data Platform API',
    url='https://github.com/SAEONData/ODP-Client',
    author='Mark Jacobson',
    author_email='mark@saeon.ac.za',
    license='MIT',
    packages=find_packages(),
    python_requires='~=3.8',
    install_requires=[
        'authlib',
        'requests',
    ],
)
