FROM amazonlinux:2

WORKDIR /var/task/watermark


ENTRYPOINT ["/var/task/bootstrap"]

