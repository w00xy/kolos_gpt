FROM ubuntu:latest
LABEL authors="vladt"

ENTRYPOINT ["top", "-b"]