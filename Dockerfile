FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SDL_VIDEODRIVER=dummy \
    SDL_AUDIODRIVER=dummy

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py database.py ./

EXPOSE 22867

CMD ["python", "server.py"]
