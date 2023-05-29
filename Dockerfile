# Base image
FROM python:3.9

# Set the working directory
WORKDIR /app
ENV PYTHONPATH=/usr/local/app/

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the working directory
COPY . /app
COPY gql/app.py /app/app.py

# Expose the port your GraphQL API will be listening on
EXPOSE 5000

# Set the entrypoint command to start your GraphQL API
CMD ["python", "app.py"]
