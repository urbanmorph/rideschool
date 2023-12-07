import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
bind = "unix:altmo_rideschool.sock"
umask = 0o007
# reload = True

# logging
accesslog = "/var/log/gunicorn/altmo_rideschool_access.log"
errorlog = "/var/log/gunicorn/altmo_rideschool_error.log"
loglevel = "debug"
