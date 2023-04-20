FROM python:3.10
LABEL maintainer="jhnnsrs@gmail.com"


# Install dependencies
RUN pip install "arkitekt[cli]==0.4.83"
RUN pip install "reaktion==0.1.16"


RUN mkdir /workspace
ADD . /workspace
WORKDIR /workspace

CMD python run.py



