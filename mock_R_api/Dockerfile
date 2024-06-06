# Use the official R base image
FROM r-base:latest

# Install dependencies for plumber including libsodium
RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libsodium-dev

# Install plumber package
RUN R -e "install.packages('plumber', repos='http://cran.us.r-project.org')"

# Create a directory for the app
RUN mkdir /app

# Copy the R scripts into the container
COPY app.R /app/app.R
COPY endpoints.R /app/endpoints.R

# Set the working directory
WORKDIR /app

# Expose the port the app runs on
EXPOSE 8002

# Run the R script when the container launches
CMD ["Rscript", "app.R"]



# IMAGE_TAG=0.0.1; docker build -t bouldermaettel/standardizedner-app3:$IMAGE_TAG . ; docker push bouldermaettel/standardizedner-app3:$IMAGE_TAG; 