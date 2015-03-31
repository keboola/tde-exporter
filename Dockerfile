FROM keboola/base
MAINTAINER Tomas Kacur <tomas.kacur@keboola.com>

# setup the environment
WORKDIR /tmp
RUN yum -y install wget git tar
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python get-pip.py
RUN pip install PyYaml

# prepare the container
WORKDIR /home
RUN git clone https://github.com/keboola/docker-tde-eporter.git ./
WORKDIR libs
RUN tar xvzf TDE-API-Python-Linux-64Bit.gz
WORKDIR DataExtract-8300.15.0308.1149
RUN python setup.py build
RUN python setup.py install
#RUN cd /home
#ENTRYPOINT python ./src/manager.py --data=/data
