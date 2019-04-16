FROM python:3.7.3

LABEL maintainer="Seokju Hong <seokju@pubg.com>"

WORKDIR /root

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.14.0/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

COPY flush.py .

ENTRYPOINT [ "python", "./flush.py", "80" ]