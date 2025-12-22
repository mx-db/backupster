[![Docker Image CI](https://github.com/mx-db/backupster/actions/workflows/docker-build.yml/badge.svg?branch=main)](https://github.com/mx-db/backupster/actions/workflows/docker-build.yml)

# Backupster

Simple and opinionated backup workflow implementation. Intended for backing up file-based application data from usually k8s-based applications to cloud storage (e.g. GCP GCS). Should be used complimentary to actual backup mechnisms like database backup. This only ensures that on full loss of the application/database, application data is still not lost.
The basic workflow looks as follows:
Backup source creates the files the backup consits of inside a specified directory ("backup directory", default .backup) -> all directories inside that backup directoy are zipped -> all files on the first level of that directory are encrypted via GPG (public key is retrieved before from the configured backup destination) -> all files encrypted that way are uploaded to a timestamped directory in the configured backup destination
