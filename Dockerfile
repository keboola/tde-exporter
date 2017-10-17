FROM php:5.5.38-alpine

RUN apk update && \
    apk upgrade && \
    apk add --update git python curl

RUN curl https://bootstrap.pypa.io/get-pip.py > get-pip.py
RUN python get-pip.py

RUN pip install -U PyYaml pytest httplib2

ADD . /code
WORKDIR /code/libs
RUN tar xvzf TDE-API-Python-Linux-64Bit.gz
WORKDIR DataExtract-8300.15.0308.1149
RUN python setup.py build
RUN python setup.py install

RUN cd \
  && curl -sS https://getcomposer.org/installer | php \
  && ln -s /root/composer.phar /usr/local/bin/composer

WORKDIR /code/php
RUN composer install --no-interaction

WORKDIR /code
ENTRYPOINT python -u ./src/main.py --data=/data

