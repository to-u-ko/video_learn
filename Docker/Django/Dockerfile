# uwsgiがpython3.9以下でしか使えず、whisperがpython3.8以上しか使えない様子のため、3.9に設定
FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu20.04 
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime
RUN apt-get update && \
    apt-get install -y python3-pip python3-dev default-libmysqlclient-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
RUN apt update
RUN apt install -y ffmpeg
# RUN apt install -y libcudnn8*
RUN apt-get install -y locales
RUN locale-gen ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8

WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
