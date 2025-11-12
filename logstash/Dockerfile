FROM docker.elastic.co/logstash/logstash:8.10.4

# Ensure geoip and useragent filters available
RUN logstash-plugin install logstash-filter-geoip logstash-filter-useragent

COPY pipeline.conf /usr/share/logstash/pipeline/logstash.conf
