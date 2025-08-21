FROM python:3.12.11-alpine3.22

EXPOSE 5000

ADD requirements.txt /
RUN pip install -r requirements.txt

ADD common.py /
ADD rest_logging.py /
ADD rest_scene.py /
ADD database_api.py /


CMD [ "python", "./database_api.py" ]