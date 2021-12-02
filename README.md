# Запуск:
docker-compose up --build

docker exec -it analyzer_social_media_flask_1 bash

gunicorn -w 4 -b 0.0.0.0:5000 main:app --reload
- PYTHONBUFFERED=True  # for print in bash ( docker-compose)

command: flask run --host=0.0.0.0

