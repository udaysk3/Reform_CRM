FROM python:3.10-alpine

EXPOSE 8000
WORKDIR /app 

COPY requirements.txt /app
RUN pip3 install -r requirements.txt --no-cache-dir

COPY . /app

COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000","-w 4", "reform_crm.wsgi"]