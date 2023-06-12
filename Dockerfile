FROM python:3.9

ADD script.sh .
ADD main.py .
ADD entrypoints.sh .

# install cron
RUN apt-get update && apt-get install cron -y
RUN pip install requests

# create two test applications that we will launch using cron
RUN chmod +x ./script.sh

# register cron jobs to start the applications and redirects their stdout/stderr
# to the stdout/stderr of the entry process by adding lines to /etc/crontab
RUN echo "*/2 * * * * root /script.sh > /proc/1/fd/1 2>/proc/1/fd/2" >> /etc/crontab

# start cron in foreground (don't fork)
ENTRYPOINT [ "/bin/bash", "/entrypoints.sh" ]