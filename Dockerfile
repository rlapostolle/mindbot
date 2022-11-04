FROM python:3.10

# set the working directory in the container
WORKDIR /mindbot

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY *.py ./

# command to run on container start
CMD [ "python", "./mindbot.py" ]