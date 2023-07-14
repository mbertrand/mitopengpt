FROM python:3.11.4


# pip
RUN curl --silent --location https://bootstrap.pypa.io/get-pip.py | python3 -
RUN pip install -U pip-tools

# Add, and run as, non-root user.
RUN mkdir /app
RUN adduser --disabled-password --gecos "" mitodl

# Install project packages
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Add project
COPY . /app
WORKDIR /app
RUN chown -R mitodl:mitodl /app

