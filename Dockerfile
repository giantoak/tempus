FROM ubuntu:14.04
MAINTAINER Sam Zhang <sam.zhang@giantoak.com>

RUN apt-get update -y
RUN apt-get build-dep build-essential -y

# Install Python dependencies
RUN apt-get install python-setuptools -y
RUN apt-get install python-dev -y

# Install pip
RUN easy_install pip

COPY . /src

# Add and install Python modules
RUN cd /src && \
    pip install -r requirements.txt 

# Expose
EXPOSE 8080
