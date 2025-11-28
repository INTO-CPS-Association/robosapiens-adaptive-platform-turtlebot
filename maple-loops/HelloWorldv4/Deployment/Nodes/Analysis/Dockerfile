FROM python:3.10
ENV PYTHONUNBUFFERED 1

WORKDIR /app

ENV PYTHONPATH="/app:{$PYTHONPATH}"

# COPY ../../../Realization /app/

COPY . .

RUN pip3 install --no-cache-dir -r Deployment/Options/Option2/PC1/requirements.txt

CMD ["python3", "Deployment/Nodes/Analysis/Analysis.py"]

