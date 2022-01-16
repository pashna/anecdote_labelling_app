FROM python:3.9.1

ENV DASH_DEBUG_MODE True
RUN apt update
COPY app app
WORKDIR app
RUN ls
RUN pip3 install -r requirements.txt
CMD ["python", "server.py"]
