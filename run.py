from app import app
from runconfig import port

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=port)
