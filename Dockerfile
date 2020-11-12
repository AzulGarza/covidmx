FROM python:3.7.2

# Install requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

RUN pip install jupyterlab

RUN apt-get -qq update && apt-get install -y build-essential \
    libssl-dev groff \
    && rm -rf /var/lib/apt/lists/*
