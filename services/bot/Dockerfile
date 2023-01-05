FROM python:3.9-slim

# set environment variables
# prevent Python from writing pyc files for dev environment
ENV PYTHONDONTWRITEBYTECODE 1
# keep Python from buffering stdin/stdout
ENV PYTHONUNBUFFERED 1
# assign default python directory
ENV PYTHONPATH /usr/src/app

# set workdir
WORKDIR /usr/src/app

# create .0L dir
RUN mkdir -p /root/.0L
COPY assets/0L.toml /root/.0L/

# copy binaries
COPY ./bin /usr/src/app/bin

# make executable
RUN chmod +x /usr/src/app/bin/ol

# add ol path to PATH
ENV PATH "$PATH:/usr/src/app/bin"

# copy .certs dir
COPY ./.certs /root/.certs

# install dependencies
RUN apt-get update && apt-get install -y netcat

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# copy app
COPY ./src /usr/src/app/src
COPY ./bot.py /usr/src/app
# COPY ./_test_bot.py /usr/src/app

# ENTRYPOINT ["tail", "-f", "/dev/null"]
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

# run karma-bot
# CMD ["python3", "_test_bot.py"]
CMD ["python3", "bot.py", "1"]
