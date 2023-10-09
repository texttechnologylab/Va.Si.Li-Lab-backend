FROM python:3.8

ADD rest-datasaver.py /
ADD ConvertAudio.py /
ADD chatgpt.py /
ADD Text2Speech.py /
ADD whisper2text.py /
ADD config.json /mnt/rawindra/ssd4/public/bagci/Speech2Text/
ADD config_chatgpt.json /mnt/rawindra/ssd4/public/bagci/Speech2Text/
ADD requirements.txt /

RUN pip install -r requirements.txt
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y ffmpeg

CMD [ "python", "./rest-datasaver.py" ]
