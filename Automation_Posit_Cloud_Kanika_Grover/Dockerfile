# Use an official Selenium image
FROM selenium/standalone-chrome:4.0.0

# Switch to root user to ensure permissions for package installations
USER root

# Install Python and required packages
RUN apt-get update && apt-get install -y \
    xvfb \
    python3 \
    python3-pip \
    && pip3 install selenium

# Set up virtual display for headless Chrome
ENV DISPLAY=:99

# Create a directory for your app
WORKDIR /app

# Copy your Python script into the container
COPY automated_test_posit_cloud.py .

# Set the entrypoint to run the Python script with the username and password
# ENTRYPOINT ["python3", "automated_test_posit_cloud.py"]

