FROM debian:bookworm-slim
ARG HADOOP_VERSION=3.3.6
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
    HADOOP_HOME=/opt/hadoop \
    HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop \
    PATH=/opt/hadoop/bin:/opt/hadoop/sbin:$PATH \
    HADOOP_OPTS=-Djava.library.path=/opt/hadoop/lib/native
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jdk-headless python3 python3-psycopg2 openssh-server openssh-client \
    ca-certificates curl tar procps time && \
    rm -rf /var/lib/apt/lists/* && \
    curl -fL --retry 3 "https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz" \
      -o /tmp/hadoop.tgz && \
    mkdir -p /opt/hadoop && tar -xzf /tmp/hadoop.tgz --strip-components=1 -C /opt/hadoop && \
    rm /tmp/hadoop.tgz && mkdir -p /run/sshd /data/output /shared-ssh && \
    printf 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64\n' >> /opt/hadoop/etc/hadoop/hadoop-env.sh && \
    printf 'mapreduce.framework.name=local\n' > /etc/datamart-mode
COPY mapreduce/ /opt/datamart/mapreduce/
COPY scripts/ /opt/datamart/scripts/
COPY hadoop/entrypoint.sh /opt/datamart/entrypoint.sh
RUN chmod +x /opt/datamart/entrypoint.sh && \
    printf '<configuration><property><name>fs.defaultFS</name><value>file:///</value></property></configuration>\n' > /opt/hadoop/etc/hadoop/core-site.xml && \
    printf '<configuration><property><name>mapreduce.framework.name</name><value>local</value></property><property><name>mapreduce.job.reduces</name><value>1</value></property></configuration>\n' > /opt/hadoop/etc/hadoop/mapred-site.xml && \
    sed -i 's/^#*PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config && \
    sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    printf 'PubkeyAuthentication yes\nPermitRootLogin prohibit-password\nPasswordAuthentication no\n' >> /etc/ssh/sshd_config
WORKDIR /opt/datamart
EXPOSE 22
ENTRYPOINT ["/opt/datamart/entrypoint.sh"]

