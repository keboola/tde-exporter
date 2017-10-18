FROM php:5.6

# setup the environment
WORKDIR /tmp
# RUN yum install -y yum-plugin-ovl
RUN apt-get update && apt-get install -y wget git tar python
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python get-pip.py
RUN pip install PyYaml
RUN pip install -U pytest
RUN pip install httplib2

# install composer
RUN cd \
  && curl -sS https://getcomposer.org/installer | php \
  && ln -s /root/composer.phar /usr/local/bin/composer


# prepare the container

ADD . /home
WORKDIR /home

WORKDIR libs
RUN tar xvzf TDE-API-Python-Linux-64Bit.gz
WORKDIR DataExtract-8300.15.0308.1149
RUN python setup.py build
RUN python setup.py install

#prepare php stuff
WORKDIR /home/php
RUN composer install --no-interaction

WORKDIR /home
#RUN PYTHONPATH=. py.test
#remove the tests results
#RUN rm -rf /tmp/pytest-of-root/
CMD python -u ./src/main.py --data=/data
