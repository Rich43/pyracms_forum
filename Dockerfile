FROM python:latest

# We copy this file first to leverage docker cache
COPY ./requirements.txt /code/forum/requirements.txt

WORKDIR /code/forum

RUN pip install -r requirements.txt

COPY . /code/forum

RUN python setup.py bdist_wheel

