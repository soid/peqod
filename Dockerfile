FROM python:3.8

ENV PYTHONUNBUFFERED 1
RUN mkdir /CUGraphWeb
WORKDIR /CUGraphWeb
ADD requirements.txt /CUGraphWeb/
RUN pip install --upgrade pip && pip install -r requirements.txt
ADD . /CUGraphWeb/

# add volume /Users/soid/Dropbox/Code/2020/columbia-catalog-data to /columbia-catalog-data
# use Volume Bindings tab in IntelliJ
