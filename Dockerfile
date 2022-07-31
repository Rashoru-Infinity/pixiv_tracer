FROM python:3-slim
COPY . /app/
RUN pip3 install --upgrade pip && \
    pip3 install --disable-pip-version-check aiohttp
CMD ["python3", "/app/run.py"]