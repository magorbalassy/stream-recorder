# Stream recorder

A containerized tool to scrape video streams in a scheduled manner.  
Schedule video stream recordings on your NAS instead the TV Box.

https://hub.docker.com/repository/docker/magorbalassy/stream-recorder

Usage:   
`docker run -p 8888:80 -v /tmp/data:/data -v /tmp/config:/config magorbalassy/stream-recorder`

## Configuration

Container volumes:  
- `/data` - is the default scrape destionation folder (recordings will end up here). Customizable with environement variable `DATA_DIR`   
- `/config` - is the config folder, the SQLite database with recording jobs is kept here, setup with environment variable CONFIG_DIR

Database:  
The status of the database can be verified by querying the `/check_db` endpoint inside the container, or `/api/check_db` thorugh Nginx (on the host machine). 

Old jobs:
- will not be scheduled duriong load 
- must be deleted manually, no automatic removal so that URLs can be reused from the UI.

**Mount the required volumes into the container.**

Ports: 
- backend of the app is running inside the container on port 5000, this doesn't have to be exposed
- `nginx` is running on port 80, this port has to be made accessible on the host machine, and Nginx will route UI requests to the backend

Map port 80 to a port on the host.

## Dockerfile

Based on the official `nginx` image, it has `Python3` and `pip` added, plus the required app libraries and files are copied as well.  
The `nginx` entrypoint is preserved, it's updated to launch `gunicorn` serving the app in the backend.  
Nginx will route requests coming to `/` to the frontend, requests from the frontend going to `/api` is routed to the backend.  

