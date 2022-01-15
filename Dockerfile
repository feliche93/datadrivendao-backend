FROM prefecthq/prefect:latest-python3.9

WORKDIR /datadrivendao

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# COPY /setup.py ./setup.py
# RUN pip install .

COPY /flows ./flows

ENV PYTHONPATH "$PYTHONPATH:./flows"
