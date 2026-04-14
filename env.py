import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL        = os.environ['DATABASE_URL']
DASHBOARD_PASSWORD  = os.environ['DASHBOARD_PASSWORD']
TIMEZONE            = os.environ.get('TIMEZONE', 'America/New_York')
