FROM python:3.10
LABEL maintainer="jhnnsrs@gmail.com"


# Install dependencies
RUN pip install "arkitekt[all]==0.5.56"


RUN mkdir /workspace
ADD . /workspace
WORKDIR /workspace



