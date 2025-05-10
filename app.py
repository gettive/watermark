import boto3
from PIL import Image
from io import BytesIO
import os

s3 = boto3.client('s3')


TARGET_BUCKET = os.environ["TARGET_BUCKET"]
WATERMARK_KEY = os.environ["WATERMARK_KEY"]

def add_watermark(source_bucket, object_key):
    # Load source image
    source_resp = s3.get_object(Bucket=source_bucket, Key=object_key)
    image = Image.open(BytesIO(source_resp['Body'].read())).convert("RGBA")

    # Load watermark image
    watermark_resp = s3.get_object(Bucket=watermark_bucket, Key=WATERMARK_KEY)
    watermark = Image.open(BytesIO(watermark_resp['Body'].read())).convert("RGBA")

    # Resize watermark if it's too large
    image_width, image_height = image.size
    max_watermark_width = int(image_width * 0.3)
    if watermark.width > max_watermark_width:
        ratio = max_watermark_width / float(watermark.width)
        new_size = (int(watermark.width * ratio), int(watermark.height * ratio))
        watermark = watermark.resize(new_size, Image.ANTIALIAS)

    # Position watermark at bottom-right
    wm_width, wm_height = watermark.size
    x = image_width - wm_width - 10
    y = image_height - wm_height - 10

    # Paste watermark on image
    watermarked_image = image.copy()
    watermarked_image.paste(watermark, (x, y), watermark)

    # Save to buffer
    buffer = BytesIO()
    watermarked_image.convert("RGB").save(buffer, format="JPEG")
    buffer.seek(0)

    # Upload back to S3
    output_key = f"watermarked/{object_key}"
    s3.put_object(
        Bucket=TARGET_BUCKET,
        Key=output_key,
        Body=buffer,
        ContentType="image/jpeg"
    )

    return {
        'statusCode': 200,
        'body': f"Watermarked image saved to {TARGET_BUCKET}/{output_key}"
    }
        

def lambda_handler(event, context=None):
    
    for record in event["Records"]:
        source_bucket = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        result = add_watermark(source_bucket, object_key)

    return {
        "statusCode": 200,
        "body": "Files copied successfully"
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


