FROM opencpu/base
MAINTAINER Sam Zhang <sam.zhang@giantoak.com>

COPY . /src

# Our version of server.conf declares preloaded libraries
COPY server.conf /etc/opencpu/server.conf

# Install R packages
RUN cd /src && \
    R --no-save < install_r_packages.r && \
    R CMD INSTALL rlines_1.0.tar.gz --library=/usr/lib/opencpu/library/

# Restart Apache2 for OpenCPU
RUN service opencpu restart && \
    service apache2 start

EXPOSE 8004
