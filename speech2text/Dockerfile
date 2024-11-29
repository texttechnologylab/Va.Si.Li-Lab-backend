FROM docker.texttechnologylab.org/vasili/python-cuda:0.1

EXPOSE 5000

ADD common.py /
ADD speech2text.py /
ADD requirements.txt /

RUN pip install -r requirements.txt

CMD [ "python", "./speech2text.py" ]