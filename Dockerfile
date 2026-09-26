FROM public.ecr.aws/lambda/python:3.14

RUN yum update -y glib2 && \
    yum clean all

# Upgrade pip and urllib3 globally to fix security vulnerabilities in the base image
RUN pip install --no-cache-dir --upgrade pip urllib3==2.6.2

COPY requirements.txt  ./
RUN pip install --no-cache-dir --default-timeout=1000 --only-binary=:all: -r requirements.txt -t "/var/task" && \
    pip install --no-cache-dir --default-timeout=1000 --only-binary=:all: --force-reinstall --no-deps urllib3==2.6.2 -t "/var/task"

COPY src/ ./

CMD ["app.lambda_handler"]