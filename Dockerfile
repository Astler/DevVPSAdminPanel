FROM python:3.12
LABEL maintainer="vladyclaw@gmail.com"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 49999
CMD ["python3", "app.py"]