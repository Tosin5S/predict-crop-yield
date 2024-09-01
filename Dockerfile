# Use an official Python runtime as a parent image
FROM python:3.11

RUN pip cache purge

# Upgrade pip to version 24.0
RUN pip install --upgrade pip==24.0

# Set environment variables for Python
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Create a directory for the application
WORKDIR /django_nlp_integration

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Download the spaCy model
# RUN python -m spacy download en_core_web_sm

# Copy the rest of the application code
COPY . .

# Set NLTK data path if needed
ENV NLTK_DATA=/django_nlp_integration/nlp_app/data/nltk_data

# Expose port if needed
EXPOSE 80

# Command to run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
