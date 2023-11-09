FROM public.ecr.aws/lambda/python:3.11.2023.11.08.12

RUN yum clean all
RUN yum clean metadata
RUN yum update -y
RUN yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm -y
RUN yum install opus-tools -y

RUN pip install numpy
COPY app/ app/
COPY lambda_handler.py .

CMD ["lambda_handler.handler"]
