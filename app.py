import boto3
from PIL import Image
from io import BytesIO
import hashlib
import os
import urllib.request
import json


s3 = boto3.client('s3')

def get_source_image(source_bucket, source_bucket_object_key):
    source_resp = s3.get_object(Bucket=source_bucket, Key=source_bucket_object_key)
    source_image = Image.open(BytesIO(source_resp['Body'].read())).convert("RGBA")

    return source_image

def get_watermark(bucket, key, max_watermark_width):
    watermark_resp = s3.get_object(Bucket=bucket, Key=key)
    watermark = Image.open(BytesIO(watermark_resp['Body'].read())).convert("RGBA")

    if watermark.width > max_watermark_width:
        ratio = max_watermark_width / float(watermark.width)
        new_size = (int(watermark.width * ratio), int(watermark.height * ratio))
        watermark = watermark.resize(new_size, Image.ANTIALIAS)

    return watermark

def add_watermark(source_image, target_bucket, watermark, position_x, position_y):
    watermarked_image = source_image.copy()
    watermarked_image.paste(watermark, (position_x, position_y), watermark)

    # Save to buffer
    buffer = BytesIO()
    watermarked_image.convert("RGB").save(buffer, format="JPEG")
    buffer.seek(0)

    encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return encoded_image
        

def lambda_handler(event, context=None):

    data = json.loads(event['body'])

    source_bucket = data['source_bucket'] 
    source_bucket_object_key = data['source_bucket_object_key']
    watermark_bucket = data['watermark_bucket']
    watermark_bucket_object_key = data['watermark_bucket_object_key']
    watermark_position_top = float(data['watermark_position_top'].strip('%')) / 100
    watermark_position_left = float(data['watermark_position_left'].strip('%')) / 100
    watermark_size_height = float(data['watermark_size_height'].strip('%')) / 100
    watermark_size_width = float(data['watermark_size_width'].strip('%')) / 100
    
    source_image = get_source_image(source_bucket, source_bucket_object_key)

    source_image_width, source_image_height = source_image.size
    width = source_image_width * watermark_size_width
    watermark = get_watermark(watermark_bucket, watermark_bucket_object_key, width)

    position_x = source_image_width * (watermark_position_left + (0.5 * watermark_size_width))
    position_y = source_image_height * (watermark_position_top + (0.5 * watermark_size_height))
    watermarked_image = add_watermark(source_image, target_bucket, watermark, position_x, position_y)

    return {
        "statusCode": 200,
        "body": "Watermark Added successfully",
        "data": {
            "watermarkedImage": watermarked_image
        }
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


