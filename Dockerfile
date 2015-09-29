FROM python:2.7.10

ADD requirements.txt /
ADD web/ /web
RUN pip install -r /requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--log-level", "INFO", "--logger-class=simple", "--pythonpath", "web", "--access-logfile", "-", "--error-logfile", "-", "--log-file", "-", "url:app"]