# About

Use this as a lambda function that gets triggered when one uploads items to your AWS S3 buckets. Use it to scan the items uploaded to your AWS S3 buckets for virus. It returns true if a virus is found and false otherwise

# Usage

Here is a sample object;
```
{
    source_bucket: 'mediaspaces-safe-original',
    source_bucket_object_key: 'users/317fe6a5-4e0c-4bc2-ab53-96da58e70094/spaces/7321ef5e-1743-4325-b63c-0953146601c0/resident/e4ad226b-2800-4ee9-931f-879334447f7e.jpg',
    target_bucket: 'mediaspaces-watermarked',
    watermark_bucket: 'mediaspaces-safe-original',
    watermark_bucket_object_key: 'watermarks/users/317fe6a5-4e0c-4bc2-ab53-96da58e70094/spaces/90cf442f-60fa-49da-9844-bcab0bedf219/fbd3abea-38de-4e85-a7c6-6df9363eb8ba.webp',
    watermark_position_top: '71.10%',
    watermark_position_left: '55.84%',
    watermark_size_height: '20.00%',
    watermark_size_width: '40.00%'
}
```

You can create the following sample request using the object shown above;

```
curl -X POST -H "Content-Type: application/json" https://0sztlfuaw0.execute-api.us-east-1.amazonaws.com/v1/watermark '{"source_bucket":"mediaspaces-safe-original","source_bucket_object_key":"users/317fe6a5-4e0c-4bc2-ab53-96da58e70094/spaces/7321ef5e-1743-4325-b63c-0953146601c0/resident/e4ad226b-2800-4ee9-931f-879334447f7e.jpg","target_bucket":"mediaspaces-watermarked","watermark_bucket":"mediaspaces-safe-original","watermark_bucket_object_key":"watermarks/users/317fe6a5-4e0c-4bc2-ab53-96da58e70094/spaces/90cf442f-60fa-49da-9844-bcab0bedf219/fbd3abea-38de-4e85-a7c6-6df9363eb8ba.webp","watermark_position_top":"71.10%","watermark_position_left":"55.84%","watermark_size_height":"20.00%","watermark_size_width":"40.00%"}'
```
