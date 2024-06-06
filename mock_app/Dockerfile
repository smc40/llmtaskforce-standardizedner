# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install any needed packages
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code into the container
COPY app.py /app/app.py

# Expose port 8000 for the Shiny app
EXPOSE 8002

# Command to run the application
CMD ["python", "app.py"]


# IMAGE_TAG=0.0.1; docker build -t bouldermaettel/standardizedner-app2:$IMAGE_TAG . ; docker push bouldermaettel/standardizedner-app2:$IMAGE_TAG; 
# docker run -p 8002:8002 bouldermaettel/standardizedner-app2:0.0.1