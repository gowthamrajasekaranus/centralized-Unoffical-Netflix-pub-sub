#Docker File to specify the python version, working directory, library installation commands.
FROM python:3.8
ADD . /app
WORKDIR /app
RUN pip install flask
RUN pip install pymongo
RUN pip install requests