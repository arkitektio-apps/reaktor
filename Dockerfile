FROM python:3.10
LABEL maintainer="jhnnsrs@gmail.com"


# Install dependencies
RUN pip install "arkitekt[cli,scheduler]==0.4.107"


RUN mkdir /workspace
ADD . /workspace
WORKDIR /workspace

CMD python run.py



