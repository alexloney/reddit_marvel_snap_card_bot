FROM python:3.9-slim-bullseye

RUN python3 -m venv /opt/venv

# Install dependencies
COPY requirements.txt .
RUN . /opt/venv/bin/activate && pip install -r requirements.txt

# Run the application:
ADD snap_bot /snap_bot
CMD . /opt/venv/bin/activate && exec python /snap_bot/main.py