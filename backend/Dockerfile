FROM python:3.9-slim

LABEL maintainer=akiyashkin@gmail.com

WORKDIR /app
COPY Pipfile .
COPY Pipfile.lock .
RUN python -m pip install --upgrade pip
RUN python -m pip install pipenv
ENV PIPENV_VENV_IN_PROJECT=1
RUN pipenv sync
COPY . .

RUN ls -lah

RUN chmod u+x bootstrap.sh
CMD ["./bootstrap.sh"]
EXPOSE 8000