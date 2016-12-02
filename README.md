# sdx-downstream-ctp

The sdx-downstream-ctp app is used within the Office for National Statistics (ONS) for consuming decrypted Survey Data Exchange (SDX) Surveys from sdx-store and delivering them to CTP.

## Installation

Using virtualenv and pip, create a new environment and install within using:

    $ pip install -r requirements.txt

To run the tests, also install the test dependencies into a virtualenv using:

    $ pip install -r test_requirements.txt

It's also possible to install within a container using docker. From the sdx-downstream directory:

    $ docker build -t sdx-downstream .

## Configuration

The following envioronment variables can be set:

`SDX_STORE_URL` - The URL of the sdx-store service, defaults to http://sdx-store:5000

`SDX_TRANSFORM_CTP_URL` - The URL of the sdx-transform-cs service, defaults to http://sdx-transform-ctp:5000

`SDX_SEQUENCE_URL` - The URL of the sdx-transform-cs service, defaults to http://sdx-sequence:5000
