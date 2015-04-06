FROM ubuntu:14.04
MAINTAINER Sam Zhang <sam.zhang@giantoak.com>

RUN apt-get update -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y -q python-software-properties software-properties-common

gpg --keyserver pgpkeys.mit.edu --recv-key 51716619E084DAB9
gpg -a --export 51716619E084DAB9 | apt-key add -

RUN add-apt-repository "deb http://cran.rstudio.com/bin/linux/ubuntu trusty/" -y
RUN apt-get update -y

RUN apt-get build-dep build-essential -y

# Bundle app source
COPY . /src


# Install R
RUN apt-get install r-base r-base-dev littler -y --force-yes --fix-missing

RUN add-apt-repository ppa:opencpu/opencpu-1.4 -y
RUN apt-get update -y


# Haven't tested this command
RUN apt-get install opencpu -y
RUN apt-get install rstudio-server -y #optional

RUN cd /src; R --no-save < install_r_packages.r
RUN cd /src; R CMD INSTALL rlines_1.0.tar.gz --library=/usr/lib/opencpu/library/
RUN service apache2 restart

RUN r install_r_packages.r
# Install Python Setuptools
RUN apt-get install python-setuptools -y

# Install pip
RUN easy_install pip

# Add and install Python modules
COPY requirements.txt /src/requirements.txt
RUN cd /src; pip install -r requirements.txt

# Expose
EXPOSE  5000

# Run
CMD ["python", "/src/run.py"]
