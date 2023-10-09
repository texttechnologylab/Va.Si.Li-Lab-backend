FROM python:3.8

ADD chatbot-host.py /
ADD requirements.txt /

RUN pip install -r requirements.txt

RUN useradd -u 8877 chatbothost

USER chatbothost

EXPOSE 5000

CMD ["python", "./chatbot-host.py"]