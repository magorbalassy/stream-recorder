# Stream Recorder

Docker setup based on:
https://blog.cloudboost.io/developing-angular-applications-using-docker-6f4835a75195


Build

docker build -t stream-recorder:0.0.2 .

Run

docker run -d -p 4200:4200 -v "/Users/magor/Documents/Dev/stream-recorder/stream-recorder/src":/stream-recorder/src stream-recorder:0.0.2 