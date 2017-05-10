# sdx-downstream-ctp

[![Build Status](https://travis-ci.org/ONSdigital/sdx-downstream-ctp.svg?branch=develop)](https://travis-ci.org/ONSdigital/sdx-downstream-ctp)

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

| Environment Variable    | Default                               | Description
|-------------------------|---------------------------------------|----------------
| SDX_STORE_URL           | `http://sdx-store:5000`               | The URL of the `sdx-store` service
| SDX_SEQUENCE_URL        | `http://sdx-sequence:5000`            | The URL of the `sdx-sequence` service
| FTP_HOST                | `pure-ftpd`                           | FTP to monitor
| FTP_USER                | _none_                                | User for FTP account if required
| FTP_PASS                | _none_                                | Password for FTP account if required
| FTP_FOLDER              | `/`                                   | FTP folder
| FTP_HEARTBEAT_FOLDER    | `/heartbeat`                          | FTP heartbeat folder
| RABBIT_QUEUE            | `sdx-ctp-survey-notifications`        | Rabbit queue name
| RABBIT_EXCHANGE         | `message`                             | RabbitMQ exchange to use
| SFTP_HOST               | _xxx.x.x.x_                           | SFTP host      
| SFTP_PORT               | `22`                                  | SFTP port

### License

Copyright © 2016, Office for National Statistics (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE) for details.