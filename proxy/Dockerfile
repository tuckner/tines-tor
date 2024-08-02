FROM python:3.9

# Install Tor
RUN apt-get update && apt-get install -y tor torsocks
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY proxy.py proxy.py

# Start the service
CMD python3 -u proxy.py
