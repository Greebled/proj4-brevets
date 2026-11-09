FROM python:3.9-slim
LABEL maintainer="Jasper Riggs <jasr@uoregon.edu>"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod -x *.py

EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["flask_brevets.py"]
