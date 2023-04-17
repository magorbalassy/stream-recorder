import json, logging, os, requests, sched, sys, time
from peewee import *
from flask import Flask, jsonify, render_template, request
from datetime import datetime

logging.basicConfig(filename="/app/app.log", level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info('==== Starting new run ====')

# Set up scheduler
scheduler = sched.scheduler(time.time, time.sleep)

app = Flask(__name__)

# Set up data folder - for the recorded streams
if not 'DATA_DIR' in os.environ:
    DATA_DIR = '/data'
else:
    if os.path.isdir(os.environ['DATA_DIR']):
        DATA_DIR = os.environ['DATA_DIR']
    else:
        logging.error(f'{DATA_DIR} is not a valid folder.')
        exit(1)
logging.info(f'Using data dir {DATA_DIR}.')


# Set up config folder - for the Sqlite db and app logs
CONFIG_DIR = '/config'
if 'CONFIG_DIR' in os.environ:    
    if os.path.isdir(os.environ['CONFIG_DIR']):
        CONFIG_DIR = os.environ['CONFIG_DIR']
    else:
        logging.info(f'The {CONFIG_DIR} not present or is not a valid folder.')
        try:
            os.makedirs(CONFIG_DIR)
        except:
            logging.error(f'Can\'t create {CONFIG_DIR}, this is required for the db, exiting.')
            sys.exit(1)
logging.info(f'Using config dir {CONFIG_DIR}.')

app.config.update(dict(
    DATABASE=os.path.join(CONFIG_DIR, 'jobs.db'),
    DEBUG=True,
    SECRET_KEY='development key'))

db = SqliteDatabase(app.config['DATABASE'])

def custom_response(msg):
  response = jsonify(msg)
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', '*')
  response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
  return response

# Create database file and table(s)
# Run once
def create_tables():
    with db:
        db.create_tables([Jobs])
        add_job()

def load_jobs():
    pass 

# The SQLite model
class BaseModel(Model):
    class Meta:
        database = SqliteDatabase(app.config['DATABASE'])
        
class Jobs(BaseModel):
    filename = TextField()
    length = IntegerField()
    url = TextField()
    status = TextField()
    start_date = DateTimeField(default=0)
    created_on = DateTimeField(default=datetime.now)

def save_stream2(duration, name, url):
    time_elapsed = 0
    start_time_in_seconds = time.time()
    if '<datetime>' in name:
        name.replace('<datetime>', time.strftime("%Y%m%d%H%M%S",time.localtime()))
    with open(f'{name}.mp4', 'wb') as f_out:
        r = requests.get(url, headers=headers, stream=True)
        logging.info(f'Starting recording {name}, http response from stream is: ', r)
        for chunk in r.iter_content(chunk_size=1024):
            if time_elapsed > duration:
                break
            if chunk:
                f_out.write(chunk)
            time_elapsed = int(time.time() - start_time_in_seconds)

def save_stream(length, name, url):
    logging.info("Recording video...")
    filename = time.strftime("/tmp/" + "%Y%m%d%H%M%S",time.localtime())+".avi"
    file_handle = open(filename, 'wb')
    chunk_size = 1024

    start_time_in_seconds = time.time()

    time_limit = 10 # time in seconds, for recording
    time_elapsed = 0
    url="http://tv.id.iptv.uno:80/zS8g4kRjm8318/vC2AsBhqzJ318/88671"
    with requests.Session() as session:
        response = session.get(url, stream=True)
        for chunk in response.iter_content(chunk_size=chunk_size):
            if time_elapsed > time_limit:
                break
            if chunk:
                file_handle.write(chunk)
    file_handle.close()

# 404 error for non-existing URLs.
@app.errorhandler(404)
def page_not_found(e):
    template = Template('''
      Error {{ code }} : The requested page does not exist.
    ''')
    return template.render(code=404)

@app.route('/', methods=['OPTIONS'])
def return_headers():
    return custom_response('')

@app.route('/', methods=['GET'])
def home():
    jobs = [ j for j in Jobs.select() ]
    job_list = []
    for j in jobs:        
        job_list.append({
            "filename": j.filename,
            "length": j.length,
            "url": j.url,
            "status": j.status,
            "start_date": j.start_date,
            "created_on": j.created_on,
            "id": j.id            
        })
    return custom_response(job_list)


@app.route('/', methods=['POST'])
def add_job():
    job = request.json
    jobs = [ j for j in Jobs.select() ]
    for j in jobs:
        if job['filename'] == j.filename and\
           job['length'] == j.length and\
           job['url'] == j.url and\
           datetime.utcfromtimestamp(int(job['start_date'])/1000) == j.start_date :
            return custom_response('0')
    with db.atomic():
        j = Jobs.create(
            filename = job['filename'],
            length = job['length'],
            status = 'new',
            url = job['url'],
            start_date = datetime.utcfromtimestamp(int(job['start_date'])/1000)
        )
        j.save()
        return custom_response(j.id);   

@app.route('/', methods=['DELETE'])
def del_job():
    print(request.json)
    qry = Jobs.delete().where(Jobs.id == request.json['id'])
    try:
        qry.execute()
        logging.debug(f'Deleted job {request.json}.')
        return custom_response(f"{request.json['id']}")
    except:
        return custom_response(0)

@app.route('/check_db')
def check_db():
    db_file = os.path.join(CONFIG_DIR,'jobs.db')
    if not os.path.isfile(db_file):
        logging.info(f'Creating database {db_file} and the jobs table.')
        create_tables()
        return custom_response(f'Created database {db_file}.')
    else:
        logging.info(f'Found database at {db_file}.')
        return f'Using database at {db_file}.'


if __name__ == "__main__":
    check_db()
    app.run(debug=True, host='0.0.0.0', port='5000')
