# pull official base image
FROM python:3.9.14-slim-buster

# set work directory
WORKDIR /usr/src/app

# create .0L dir
RUN mkdir -p /root/.0L
COPY assets/0L.toml /root/.0L/

# copy binaries
COPY ./bin ${BIN_PATH}

# make executable
RUN chmod +x ${BIN_PATH}/ol ${BIN_PATH}/txs ${BIN_PATH}/onboard

# add ol path to PATH
ENV PATH "$PATH:/usr/src/app/bin"

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /usr/src/app

# install system dependencies
RUN apt-get update && apt-get install -y netcat libpq-dev gcc

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy app
COPY . .

# run entrypoint.sh
COPY ./entrypoint.sh /usr/src/entrypoint.sh
RUN chmod +x /usr/src/entrypoint.sh
ENTRYPOINT ["/usr/src/entrypoint.sh"]
# ENTRYPOINT ["tail", "-f", "/dev/null"]

# run main.py
CMD ["python", "main.py"]
