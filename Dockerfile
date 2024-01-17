# docker build --no-cache -t singjust/massdash:0.0.1 .
# docker push singjust/massdash:0.0.1

# MassDash Dockerfile
FROM python:3.9.1

# Set the working directory in the container
WORKDIR /massdash

# Install any needed packages specified in requirements.txt
RUN pip3 install massdash

# # Copy the current directory contents into the container at /app
# COPY . /massdash/

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Run app.py when the container launches
CMD ["massdash", "gui"]
