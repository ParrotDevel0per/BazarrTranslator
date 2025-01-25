# Use the official Python 3.11 image as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the application files to the container
COPY . /app

# Install any system dependencies if required
RUN apt-get update && apt-get install -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables as empty by default
ENV BAZARR_SERVER="" \
    BAZARR_API_KEY="" \
    RADARR_SERVER="" \
    RADARR_API_KEY="" \
    SONARR_SERVER="" \
    SONARR_API_KEY="" \
    LIBRETRANSLATE_ENABLED="" \
    LIBRETRANSLATE_SERVER=""


# Define the command to run the application
CMD ["python3", "main.py"]
