FROM public.ecr.aws/lambda/python:3.11

RUN yum update -y glib2 && \
    yum clean all

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt  ./
RUN pip install --no-cache-dir --default-timeout=1000 --only-binary=:all: -r requirements.txt -t "/var/task"

COPY src/ ./

CMD ["app.lambda_handler"]
