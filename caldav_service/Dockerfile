FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir starlette uvicorn[standard]
COPY server.py .
ENV CALDAV_DATA_DIR=/data/calendars
EXPOSE 5232
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "5232"]
