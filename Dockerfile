FROM python:3.11-slim

WORKDIR /app

# Copy and install requirements
COPY api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy api folder (will be overridden by volume mount in development)
COPY api/ ./api/

# Make python treat /app/api as the module root
ENV PYTHONPATH="/app/api"

EXPOSE 4000

CMD ["python", "-u", "api/backend_app.py"]