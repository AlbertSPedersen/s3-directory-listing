from flask import Flask, request, render_template, redirect
from datetime import datetime
import boto3
import json


with open('config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

client = boto3.client('s3',
    endpoint_url=config['endpoint_url'],
    aws_access_key_id=config['access_key_id'],
    aws_secret_access_key=config['secret_access_key']
)
paginator = client.get_paginator('list_objects_v2')
app = Flask(__name__)


@app.before_request
def index():
    if request.path.endswith('/'):
        page_iterator = paginator.paginate(
            Bucket = config['bucket_name'],
            Delimiter = '/',
            Prefix = request.path[1:]
        )
        directories = []
        files = []
        for page in page_iterator:
            if 'CommonPrefixes' in page:
                directories += [directory['Prefix'][len(request.path[1:]):] for directory in page['CommonPrefixes']]
            if 'Contents' in page:
                files += [{'name': file['Key'][len(request.path[1:]):], 'last_modified': file['LastModified'].strftime('%Y-%m-%d %H:%M:%S'), 'size': file['Size']} for file in page['Contents'][1:]]

        return render_template('index.html', path=request.path, directories=directories, files=files)
    else:
        return redirect(config['bucket_url'] + request.path)


if __name__ == '__main__':
    app.run()
