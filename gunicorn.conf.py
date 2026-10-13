# Gunicorn reads this file automatically when started from the project folder.
# Uploading a video (up to 50 MB) on a slow connection takes longer than gunicorn's
# default 30-second limit, after which the upload would be cut off.
timeout = 300
accesslog = "-"
