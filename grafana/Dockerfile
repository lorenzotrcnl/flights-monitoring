FROM grafana/grafana-oss
WORKDIR /
USER root
RUN apk update
RUN apk add git
RUN apk add curl
RUN apk add --update nodejs npm
WORKDIR /var/lib/grafana/plugins
RUN git clone https://github.com/JamesOsgood/mongodb-grafana
WORKDIR /var/lib/grafana/plugins/mongodb-grafana
RUN npm install