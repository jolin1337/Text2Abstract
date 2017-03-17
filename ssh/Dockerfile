# Text2Abstract
#
# VERSION               0.0.2

FROM ubuntu:14.04
MAINTAINER Johannes Lindén <johannes@godesity.se>

ENV TEXT2ABSTRACT_DIR=/opt/Text2Abstract

RUN mkdir -p $TEXT2ABSTRACT_DIR
WORKDIR $TEXT2ABSTRACT_DIR

RUN apt-get update && apt-get install -y openssh-server
RUN mkdir /var/run/sshd
RUN echo 'root:screencast' | chpasswd
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]

# To build
# > docker build -t ssh_server:v1.0.0 .
# To run
# > docker run -p from-port:to-port -v c:/Users/desktop-godesity/Documents/Text2Abstract/:/opt/Text2Abstract ssh_server:v1.0.0

# To stop all containers from running (do before remove all containers)
# > docker stop $(docker ps -a -q)
# To remove all containers
# > docker rm $(docker ps -a -q)