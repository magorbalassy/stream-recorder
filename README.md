# Stream recorder

A containerized tool to scrape video streams in a scheduled manner.

## Configuration

- container volumes:  
`/data` - is the default scrape destionation folder (recordings will end up here).  
`/config` - is the config folder, the SQLite database with recording jobs is kept here

- ports: app is running inside the container on port 5000
