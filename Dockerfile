FROM python:3.9

ADD main.py .
ADD crontab /etc/cron.d/crontab

RUN apt-get update && apt-get install -y cron
RUN pip install requests

RUN chmod 0644 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab

CMD ["cron", "-f"]