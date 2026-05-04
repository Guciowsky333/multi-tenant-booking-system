FROM python:3.13.3-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install uv
RUN uv pip install --system --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]