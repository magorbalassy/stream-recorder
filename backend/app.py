import json, logging, os, requests, sys, time
from datetime import datetime
from flask import current_app, Flask, jsonify, render_template, request
from peewee import *
from threading import Timer

logging.basicConfig(filename="/dev/stdout", level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info('==== Starting new run ====')


app = Flask(__name__)

# Set up data folder - for the recorded streams
if not 'DATA_DIR' in os.environ:
    DATA_DIR = '/data'
else:
    DATA_DIR = os.environ['DATA_DIR']
logging.info(f'Using data dir {DATA_DIR}.')
if not os.path.isdir(DATA_DIR):
    logging.error(f'{DATA_DIR} is not present or it\'s not a valid folder.')
    try:
        os.makedirs(DATA_DIR)
    except:
        logging.error(f'Can\'t create {DATA_DIR}, this is required for the downloads, exiting.')
        sys.exit(1)
    logging.info(f'Created data folder {DATA_DIR}.')
if not os.access(DATA_DIR, os.W_OK):
    logging.error(f'{DATA_DIR} is not a writeable folder.')
    exit(1)

# Set up config folder - for the Sqlite db and app logs
if not 'CONFIG_DIR' in os.environ:
    CONFIG_DIR = '/config'
else:
    CONFIG_DIR = os.environ['CONFIG_DIR']
logging.info(f'Using config dir {CONFIG_DIR}.')
if not os.path.isdir(CONFIG_DIR):
    logging.info(f'The {CONFIG_DIR} not present or it\'s not a valid folder.')
    try:
        os.makedirs(CONFIG_DIR)
    except:
        logging.error(f'Can\'t create {CONFIG_DIR}, this is required for the db, exiting.')
        sys.exit(1)
    logging.info(f'Created config folder {CONFIG_DIR}.')
if not os.access(CONFIG_DIR, os.W_OK):
        logging.error(f'{CONFIG_DIR} is not a writeable folder.')
        exit(1)

app.config.update(dict(
    DATABASE=os.path.join(CONFIG_DIR, 'jobs.db'),
    DEBUG=True))
app.config['db'] = SqliteDatabase(app.config['DATABASE'])
app.config['jobs'] = []
app.config['job_timers'] = {}

def json_response(msg):
  response = jsonify(msg)
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', '*')
  response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
  return response

# Create database file and table(s)
# Run once
def create_tables():
    with app.config['db'] as db:
        db.create_tables([Jobs])

def load_jobs():
    jobs = [ j for j in Jobs.select() ]
    json_jobs = []
    for j in jobs:        
        json_jobs.append({
            "filename": j.filename,
            "length": j.length,
            "url": j.url,
            "status": j.status,
            "start_date": j.start_date,
            "created_on": j.created_on,
            "id": j.id            
        })
        with app.app_context():
            scheduler(j)
            logging.debug(f'{app.config}')
    return json_jobs

def get_ts():
    return int(datetime.now().strftime('%s'))*1000

def scheduler(j):
    if j.id not in app.config['job_timers']:
        now = get_ts()
        if now > j.start_date:
            logging.info(f'Job with ID {j.id} has a start date in the past, can\'t be scheduled.')
            return False
        else:
            start_in_seconds = (j.start_date - now)/1000
            logging.info(f'Time until schedule: {start_in_seconds} seconds.')
            t = Timer(start_in_seconds, save_stream, [j.length * 60, j.filename, j.url])
            t.start()
            with app.app_context():
                app.config['job_timers'][j.id] = "t"
            logging.info(f'Scheduled job with id {j.id}.')
    else:
        logging.debug(f'Job with {j.id} id is already scheduled.')

# The SQLite model
class BaseModel(Model):
    class Meta:
        database = SqliteDatabase(app.config['DATABASE'])
        
class Jobs(BaseModel):
    filename = TextField()
    length = IntegerField()
    url = TextField()
    status = TextField()
    start_date = IntegerField()
    created_on = DateTimeField(default=datetime.now)

# Save to MP4
def save_stream(duration, name, url):
    time_elapsed = 0
    start_time_in_seconds = time.time()
    if '<datetime>' in name:
        name.replace('<datetime>', time.strftime("%Y%m%d%H%M%S",time.localtime()))
    with open(f'{DATA_DIR}/{name}.mp4', 'wb') as f_out:
        r = requests.get(url, headers=headers, stream=True)
        logging.info(f'Starting recording {name}, http response from stream is: ', r)
        for chunk in r.iter_content(chunk_size=1024):
            if time_elapsed > duration:
                break
            if chunk:
                f_out.write(chunk)
            time_elapsed = int(time.time() - start_time_in_seconds)

# 404 error for non-existing URLs.
@app.errorhandler(404)
def page_not_found(e):
    template = Template('''
      Error {{ code }} : The requested page does not exist.
    ''')
    return template.render(code=404)

@app.route('/', methods=['OPTIONS'])
def return_headers():
    return json_response('')

@app.route('/', methods=['GET'])
def home():
    return json_response(load_jobs())

@app.route('/', methods=['POST'])
def add_job():
    job = request.json
    jobs = [ _ for _ in Jobs.select() ]
    for j in jobs:
        if job['filename'] == j.filename and\
           job['length'] == j.length and\
           job['url'] == j.url and\
           int(job['start_date']) == j.start_date :
            return json_response('0')
    with app.config['db'].atomic():
        j = Jobs.create(
            filename = job['filename'],
            length = job['length'],
            status = 'new',
            url = job['url'],
            start_date = int(job['start_date'])
        )
        j.save()
        with app.app_context():
            scheduler(j)
        return json_response(j.id);   

@app.route('/', methods=['DELETE'])
def del_job():
    qry = Jobs.delete().where(Jobs.id == request.json['id'])
    try:
        qry.execute()
    except:
        logging.info(f'An error occurred while removing job {request.json}.')
        return json_response(0)
    logging.info(f'Deleted job {request.json}.')
    if request.json['id'] in app.config['job_timers']:
        app.config['job_timers'][request.json['id']].cancel()
        logging.info(f'Cancelled scheduled job {request.json}.')
    return json_response(f"{request.json['id']}")

@app.route('/check_db')
def check_db():
    db_file = app.config['DATABASE']
    if not os.path.isfile(db_file):
        logging.info(f'Database not found. Creating database {db_file} and the jobs table.')
        try:
            create_tables()
        except:
            logging.error(f'Could not create database at {db_file}.')
            logging.error(f'Call endpoint /check_db to retry recreating the database.')
            return f'Failed to create database at {db_file}. Verify that folder is writable.'
        return f'Created database {db_file}.'
    else:
        logging.info(f'Found database at {db_file}.')
        return f'Using database at {db_file}.'

check_db()
load_jobs()
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5000')
