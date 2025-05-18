# Use the official lightweight Python image.
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY bet_agent_v2.py .

# Expose the port Flask is running on
EXPOSE 8080

# Run the Flask app
CMD ["python", "bet_agent_v2.py"]
