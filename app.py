import boto3
from PIL import Image
from io import BytesIO
import hashlib
import os
import urllib.request
import json
import base64


s3 = boto3.client('s3')
SOURCE_BUCKET = os.environ["SOURCE_BUCKET"]
WATERMARK_BUCKET = os.environ["WATERMARK_BUCKET"]

def get_source_image(source_bucket_object_key):
    source_resp = s3.get_object(Bucket=SOURCE_BUCKET, Key=source_bucket_object_key)
    source_image = Image.open(BytesIO(source_resp['Body'].read())).convert("RGBA")

    return source_image

def get_watermark(watermark_bucket_object_key, watermark_width, watermark_height):
    watermark_resp = s3.get_object(Bucket=WATERMARK_BUCKET, Key=key)
    watermark = Image.open(BytesIO(watermark_resp['Body'].read())).convert("RGBA")

    ratio_width = watermark_width / float(watermark.width)
    ratio_height = watermark_height / float(watermark.height)
    ratio = min(ratio_width, ratio_height)

    new_size = (int(watermark.width * ratio), int(watermark.height * ratio))
    watermark = watermark.resize(new_size, Image.ANTIALIAS)

    return watermark

def add_watermark(source_image, watermark, position_x, position_y):
    watermarked_image = source_image.copy()

    x = int(position_x)
    y = int(position_y)
    watermarked_image.paste(watermark, (x, y), watermark)

    # Save to buffer
    buffer = BytesIO()
    watermarked_image.convert("RGB").save(buffer, format="JPEG")
    buffer.seek(0)

    encoded_image = None

    try:
        encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return {
            'message': 'SUCCESS',
            'data': encoded_image
        }
    except Exception as e:
        return {
            'message': 'ERROR',
            'data': f"An error occurred: {e}"
        }        

    return encoded_image
        

def lambda_handler(event, context=None):

    data = json.loads(event['body'])

    source_bucket_object_key = data['source_bucket_object_key']
    watermark_bucket_object_key = data['watermark_bucket_object_key']
    watermark_position_top = float(data['watermark_position_top'].strip('%')) / 100
    watermark_position_left = float(data['watermark_position_left'].strip('%')) / 100
    watermark_size_height = float(data['watermark_size_height'].strip('%')) / 100
    watermark_size_width = float(data['watermark_size_width'].strip('%')) / 100
    
    source_image = get_source_image(source_bucket_object_key)

    source_image_width, source_image_height = source_image.size
    width = source_image_width * watermark_size_width
    height = source_image_height * watermark_size_height
    watermark = get_watermark(watermark_bucket_object_key, width, height)

    position_x = source_image_width * watermark_position_left
    position_y = source_image_height * watermark_position_top
    response = add_watermark(source_image, watermark, position_x, position_y)

    return {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': 'https://*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Methods': 'POST',
        },
        "body": json.dumps(response)
    }


if __name__ == "__main__":
    AWS_LAMBDA_RUNTIME_API = os.environ["AWS_LAMBDA_RUNTIME_API"]
    while True:
        url = f"http://{AWS_LAMBDA_RUNTIME_API}/2018-06-01/runtime/invocation/next"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            headers = dict(response.getheaders())
            event_body = json.loads(response.read().decode())

        request_id = headers["Lambda-Runtime-Aws-Request-Id"]
        result = lambda_handler(event_body)

        payload = json.dumps(result).encode('utf-8')
        post_url = f"http://{AWS_LAMBDA_RUNTIME_API}/2018-06-01/runtime/invocation/{request_id}/response"
        post_req = urllib.request.Request(
                post_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
        with urllib.request.urlopen(post_req) as _:
            pass


