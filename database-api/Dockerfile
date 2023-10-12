FROM python:3.8

EXPOSE 5000

ADD common.py /
ADD rest_logging.py /
ADD rest_scene.py /
ADD database_api.py /
ADD config_scene.json /mnt/rawindra/ssd4/public/bagci/Speech2Text/
ADD config_logging.json /mnt/rawindra/ssd4/public/bagci/Speech2Text/
ADD requirements.txt /

RUN pip install -r requirements.txt

CMD [ "python", "./database_api.py" ]