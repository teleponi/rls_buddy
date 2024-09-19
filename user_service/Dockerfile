FROM python:3.12-slim AS build-stage

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
COPY entrypoint.sh .
RUN chmod +x /app/entrypoint.sh


# Install dependencies in a virtual environment to reduce size
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN chmod +x /app/wait-for-it.sh
RUN chmod +x /app/entrypoint.sh

# Production Stage
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Create a non-root user
RUN useradd -ms /bin/bash nonrootuser

# Set the working directory
WORKDIR /app

# Copy virtual environment and application from the build stage
COPY --from=build-stage /opt/venv /opt/venv
COPY --from=build-stage /app /app
RUN chown -R nonrootuser:nonrootuser /app
RUN chmod +x /app/wait-for-it.sh
RUN chmod +x /app/entrypoint.sh

# Change to the non-root user
USER nonrootuser

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
