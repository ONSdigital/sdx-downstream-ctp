### Unreleased
  - Add message to README now that this repo is deprecated

### 2.2.0 2017-07-25
  - Change all instances of ADD to COPY in Dockerfile
  - Remove use of SDX_HOME variable in makefile

### 2.1.0 2017-07-10
  - Update timestamp in all logs as UTC
  - Update to use async_consumer from sdx-common
  - Add common library logging
  - Add environment variables to README
  - Add correct license attribution
  - Add codacy badge
  - Add support for codecov to see unit test coverage 
  - Add logging binary filename before attempting delivery
  - Fix incorrect git merge in Dockerfile and requirements.txt

### 2.0.0 2017-03-15
  - Log version number on startup
  - Fix handling of None responses in remote call
  - Add SFTP support
  - Change `nack for retry` to `nack` for SDX logging
  - Change `status_code` to `status` for SDX logging
  - Change logging messages to add the service called or returned from

### 1.0.0 2017-02-16
  - Initial release
