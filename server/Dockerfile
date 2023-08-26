# syntax=docker/dockerfile:1

FROM python:3.11

RUN pip3 install flask flask-argon2 bleach

WORKDIR /python-docker

COPY . .

# when --debug is enabled, --no-reload is required also to prevent the
# initialisation code (which generates the admin password, etc.)
# from being executed more than once
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=80", "--debug", "--no-reload"]
