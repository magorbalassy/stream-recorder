# Records to AVI, might need to change to MP4

import time
import requests

print("Recording video...")
filename = time.strftime("stream-%Y%m%d%H%M%S",time.localtime()) + ".avi"
file_handle = open(filename, 'wb')
chunk_size = 1024

start_time_in_seconds = time.time()

# time in seconds, for recording
time_limit = 1800 
time_elapsed = 0
url="http://tv..com/stream"
with requests.Session() as session:
    response = session.get(url, stream=True)
    for chunk in response.iter_content(chunk_size=chunk_size):
        if time_elapsed > time_limit:
            break
        # to print time elapsed   
        if int(time.time() - start_time_in_seconds)- time_elapsed > 0 :
            time_elapsed = int(time.time() - start_time_in_seconds)
            print(time_elapsed, end='\r', flush=True)
        if chunk:
            file_handle.write(chunk)

    file_handle.close()