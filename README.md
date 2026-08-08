# About

This is an AWS lambda function for watermarking S3 images with other S3 images. To use it, create a docker image out of this repo (There's a dockerfile) and push to your ECR repository. Create an API gateway that invokes the created lambda function when called. This lambda function only handles post request with the data shown below;
```
{
    source_bucket: <source_bucket>,
    source_bucket_object_key: <source_bucket_object_key>,
    target_bucket: <target_bucket>,
    watermark_bucket: <watermark_bucket>,
    watermark_bucket_object_key: <watermark_bucket_object_key>,
    watermark_position_top: <watermark_position_top e.g; '71.10%'>,
    watermark_position_left: <watermark_position_left e.g; '55.84%'>,
    watermark_size_height: <watermark_size_height e.g; '20.00%'>,
    watermark_size_width: <watermark_size_width e.g; '40.00%>'
}
```

## Publishing the Docker image

The GitHub Actions workflow publishes `latest` and a commit-SHA tag to Amazon ECR Public whenever changes are pushed to `master`. Before enabling it, add these repository or environment secrets in GitHub:

- `PUBLIC_ECR_REPOSITORY`: `public.ecr.aws/i3j1t5i1/watermark`
- `AWS_ACCESS_KEY_ID`: access key for an IAM principal allowed to push to that public ECR repository
- `AWS_SECRET_ACCESS_KEY`: corresponding secret access key

The workflow authenticates to ECR Public through `us-east-1`, as required by the service. The IAM principal needs permission to obtain an ECR Public authorization token and upload image layers to the repository.
