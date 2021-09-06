FROM python:3.6.9-slim

# Copy all required files to the src folder
COPY server.py /usr/src/
COPY requirements.txt /usr/src/
COPY modules /usr/src/modules

# Install required packages
RUN pip3 install -r /usr/src/requirements.txt

# Run the server with Gunicorn
ENTRYPOINT ["gunicorn", "--worker-tmp-dir", "/dev/shm", "--worker-class", "gthread", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--chdir", "/usr/src/", "server:app"]
