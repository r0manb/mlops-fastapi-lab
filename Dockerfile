# app/Dockerfile
#базовый образ
FROM python:3.10-slim 
#рабочая директория проекта
WORKDIR /fast_app            
# RUN apt-get update && apt-get install 
COPY requirements.txt .
RUN pip3 install -r ./requirements.txt
#порт для взаимодействия с контейнером
COPY . .    
EXPOSE 8000
#
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]