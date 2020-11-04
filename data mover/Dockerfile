FROM registry.access.redhat.com/ubi8/ubi:latest
LABEL maintainer="cblum@redhat.com"

WORKDIR /
RUN yum install -y \
    https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm \
    curl \
    wget \
    rsync
COPY data-mover.sh /
ENTRYPOINT [ "./data-mover.sh" ]
