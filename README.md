# Flights Monitoring | Lambda-Architecture Implementation (API + KAFKA + SPARK + MONGO + GRAFANA)

<p align="center">
  <a href="">
    <img alt="" src="" target="_blank" />
  </a>
  
  <a href="">
    <img alt="Twitter" src="" target="_blank" />
  </a>
</p>

##### Index

* [Introduction](#intro)
* [Quickstart](#usage)
    * Start the containers
    * Check status of MongoDB Sink Kafka Connector
    * Start Grafana-Mongo Proxy
    * Start Spark ReadStream Session
    * Start data ingestion
    * Access dashboard in Grafana
* [Monitoring](#monitoring)
    * Kafka Cluster
    * Kafka-Mongo Connector
    * Spark Jobs
    * MongoDB
* [Components](#components)
* [Troubleshooting](#trouble)

<a name="intro"></a>

## Introduction

The following project was developed with the goal of implementing current leading technologies in both batch and real-time data management and analysis. The data source is FlightRadar24, a website that offers real-time flight tracking services. Through an API it is possible to obtain information, in real time, regarding flights around the globe. A dashboard will be developed to allow control over what is happening in a specific area, in addition to general analysis regarding aircrafts and airports.
The real-time characteristic of the chosen data source motivates the need to set up an architecture that can cope with the large number of data arriving in a short period of time. A lambda-like architecture was developed to make possible the ability to store data and at the same time analyze it in real time. The pipeline consists of several stages, which use current technologies for Real-Time Data Processing.
All of this was developed in a Docker environment to enable future testing and a total replication of the project.

<img src="project_pipeline.png" alt="demo"/>

<a name="usage"></a>

## Quickstart

Prepare yourself three active terminals placed in the project folder.
In the **first** one:

1. **Start the containers**

``` sh
> docker compose up -d
```

Wait about 30 seconds and run the following command:

2. **Check status of MongoDB Sink Kafka Connector**

``` sh
> curl localhost:8083/connectors/mongodb-connector/status | jq
```

If everything is running go ahead with the steps, otherwise see [Troubleshooting](#trouble) section.

3. **Start Grafana-Mongo Proxy**

``` sh
> docker exec -d grafana npm run server
```
  
If you want to see the real-time component of the project in action then execute the next two commands. Otherwise skip directly to the 6° step to view the state of the dashboard at the last commit.  
  
4. **Start Spark ReadStream Session**

In the **second** terminal:  
``` sh
> docker exec -it jupyter python spark-submit
```
  
5. **Start data ingestion**

In the **third** terminal:  
``` sh
> docker exec -it jupyter python producer.py
```
  
6. **Access the dashboard in Grafana** at **localhost:3000** \| admin@password

<a name="monitoring"></a>

## Monitoring

1. **KAFKA CLUSTER**

We need first to execute some commands to enable JMX Polling.

``` sh
> docker exec -it zookeeper ./bin/zkCli.sh
$ create /kafka-manager/mutex ""
$ create /kafka-manager/mutex/locks ""
$ create /kafka-manager/mutex/leases ""
$ quit
```

After that we can access the Kafka Manager UI at **localhost:9000**.
Click on **Cluster** and **Add Cluster**.
Fill up the following fields:

* **Cluster Name** = \<insert a name>
* **Cluster Zookeeper Hosts** = zookeeper:2181
  
Tick the following:  

* ✅ **Enable JMX Polling**
* ✅ **Poll consumer information**
  
Leave the remaining fields by default.  
Hit **Save**.  

- - -

2. **KAFKA-MONGO CONNECTOR**

To check the status of the connector and the status of related tasks, execute the following command.

``` sh
> curl localhost:8083/connectors/mongodb-connector/status | jq
```

If everything is working properly you should see a bunch of **Running**.  
Make sure you have installed **jq**, otherwise remove it from the command or install it.

- - -

3. **SPARK JOBS**

To view the activity of spark jobs, access at **localhost:4040/jobs/**.
  
- - -

4. **MONGODB**

You can interact with the db and related collections in Mongo through two options:

``` sh
1. MongoDB Compass UI
2. > docker exec -it mongodb mongo
```

<a name="components"></a>

## Components

<a name="trouble"></a>

## Troubleshooting
