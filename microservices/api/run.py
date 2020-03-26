from api import app

if __name__ == '__main__':
   app.run(app.config['HOST'],app.config['PORT'],app.config['DEBUG'])