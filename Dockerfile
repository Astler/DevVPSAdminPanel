FROM python:3.8
LABEL maintainer="vladyclaw@gmail.com"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 80
CMD ["python3", "app.py"]