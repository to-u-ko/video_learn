# uwsgiがpython3.9以下でしか使えず、whisperがpython3.8以上しか使えない様子のため、3.9に設定
FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu20.04 
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime
RUN apt-get update && \
    apt-get install -y python3.9 python3-pip && \
    apt-get install -y locales && \
    locale-gen ja_JP.UTF-8 && \
    rm -rf /var/lib/apt/lists/* 

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
#ADD requirements.txt /code/
RUN pip install faster-whisper

