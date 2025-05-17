FROM amazonlinux:2

WORKDIR /var/task

RUN yum -y update \
	&& yum -y install python3 python3-pip \
    	&& yum clean all

RUN pip3 install boto3 Pillow

COPY . .

RUN chmod -R 755 .

ENTRYPOINT ["/var/task/bootstrap"]
