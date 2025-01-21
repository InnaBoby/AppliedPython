FROM python:3.10

WORKDIR /HW2

COPY HW2/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "HW2/bot.py"]