FROM amazonlinux:2

WORKDIR /var/task

RUN yum -y update && \
    yum -y install \
    python3 \
    python3-pip \
    && yum clean all

COPY . .

RUN pip3 install -r requirements.txt -t .

ENTRYPOINT ["/var/task/bootstrap"]