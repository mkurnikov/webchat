FROM python:3.5

COPY requirements.txt /
RUN pip install -r requirements.txt

EXPOSE 8000

