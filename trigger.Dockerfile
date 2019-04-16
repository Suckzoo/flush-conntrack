FROM appropriate/curl

LABEL maintainer="Seokju Hong <seokju@pubg.com>"

RUN apk add --update curl

WORKDIR /root

COPY trigger.sh .
RUN chmod +x trigger.sh

ENTRYPOINT [ "./trigger.sh" ]