FROM docker.texttechnologylab.org/vasili/python-cuda:0.1

EXPOSE 5000

ADD common.py /
ADD speech2text.py /
ADD requirements.txt /

RUN pip install -r requirements.txt

RUN python -c "import whisper; whisper.load_model('small')"

CMD [ "python", "./speech2text.py" ]