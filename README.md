# Stream recorder

A containerized tool to scrape video streams in a scheduled manner.  

https://hub.docker.com/repository/docker/magorbalassy/stream-recorder

## Configuration

- container volumes:  
`/data` - is the default scrape destionation folder (recordings will end up here). Customizable with environement variable `DATA_DIR` 
`/config` - is the config folder, the SQLite database with recording jobs is kept here, setup with environment variable CONFIG_DIR

**Mount the required volumes into the container.**

- ports: 
    - backend of the app is running inside the container on port 5000, this doesn't have to be exposed
    - `nginx` is running on port 80, this port has to be made accessible on the host machine, and Nginx will route UI requests to the backend

Map port 80 to a port on the host.

## Dockerfile

Based on the official `nginx` image, it has `Python3` and `pip` added, plus the required app libraries and files are copied as well.  
The `nginx` entrypoint is preserved, it's updated to launch `gunicorn` serving the app in the backend.  
Nginx will route requests coming to `/` to the frontend, requests from the frontend going to `/api` is routed to the backend.  

