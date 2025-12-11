from app import create_app
import logging, os
from logging.handlers import RotatingFileHandler

app = create_app()

if not os.path.exists('logs'):
    os.makedirs('logs')
handler = RotatingFileHandler('logs/error.log', maxBytes=1000000, backupCount=3, encoding='utf-8')
handler.setLevel(logging.ERROR)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.addHandler(handler)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)