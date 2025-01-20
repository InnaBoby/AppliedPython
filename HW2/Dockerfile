FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r ./HW2/requirements.txt

COPY . .

CMD ["python", "./HW2/bot.py"]
