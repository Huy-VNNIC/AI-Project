FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better cache utilization
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Make sure the directories exist
RUN mkdir -p models
RUN mkdir -p datasets/feedback

# Make sure the entrypoint script is executable
RUN chmod +x run_estimation_service.sh

# Set up a non-root user for better security
RUN useradd -m -u 1000 user
USER user

# Expose the port the app will run on
EXPOSE 7860

# Command to run the app
CMD ["python", "app.py"]
