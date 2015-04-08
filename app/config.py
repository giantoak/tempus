import os

dburl = os.getenv('TEMPUS_DB_URL', '')
port = os.getenv('TEMPUS_PORT', 5000)

redisurl = os.getenv('TEMPUS_REDIS_URL', 'localhost')

# Environment variables set by Docker Compose
_opencpu_host = os.getenv('OPENCPU_1_PORT_80_TCP_ADDR', 'localhost')
_opencpu_port = os.getenv('OPENCPU_1_PORT_80_TCP_PORT', '80')

OPENCPUURL = 'http://' + _opencpu_host + ':' + _opencpu_port

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(APP_ROOT, 'upload')

