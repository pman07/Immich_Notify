FROM python:3.9

ADD /templates/config.html ./templates/config.html
ADD main.py .
ADD flask_app.py .
ADD notify.py .

EXPOSE 5000

RUN pip install requests schedule flask

CMD [ "python", "./main.py"]