from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType, FloatType
from pyspark.sql.functions import from_json, col, to_timestamp, window, count, udf, array
from geopy.distance import geodesic

#def write_and_info(batch_df, batch_id):
#    print("batch_id: {0}, # rows: {1}".format(batch_id, df.count()))
#    
#    batch_df.write.format('mongodb').mode('default') \
#        .option("spark.mongodb.connection.uri", "mongodb://mongodb:27017/") \
#        .option("spark.mongodb.database", "flightsDB") \
#        .option("spark.mongodb.collection", "distancesRT") \
#        .save()
    

if __name__ == '__main__':
    spark = SparkSession.builder \
        .appName("kafkastream") \
        .master('local') \
        .config("spark.jars", "org.mongodb.spark_mongo-spark-connector-10.0.5.jar") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    
    # Read the static df
    airportsDF = spark.read.format("mongodb") \
        .option("spark.mongodb.connection.uri", "mongodb://mongodb:27017/") \
        .option("spark.mongodb.database", "flightsDB") \
        .option("spark.mongodb.collection", "airports") \
        .load()
    
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka1:9092,kafka2:9092") \
        .option("subscribe", "apicall") \
        .option("startingOffsets", "latest") \
        .load()
    
    print('KAFKA STREAM SCHEMA -------------------------------------')
    df.printSchema()
    
    streamValue = df.selectExpr("CAST(value AS STRING)")
    trueschema = open('flights_schema.txt', mode='r').read()
    
    df = streamValue.select(from_json(col=col("value"), schema=eval(trueschema)).alias("data")).select("data.*")
    
    print('DATA SCHEMA -------------------------------------')
    df.printSchema()
    
    print('[READY]')
    print('[PROCESSING STREAM...]')
    
    @udf(returnType=FloatType())
    def geodesic_udf(a, b):
        return geodesic(a, b).km
    
    fl = df.join(airportsDF, df.origin_airport_iata == airportsDF.iata) \
        .select(["ts", "id", col("destination_airport_iata").alias("dest_iata"), "at_zone",
                 col("latitude").alias("craft_lat"), col("longitude").alias("craft_lon"), 
                 col("lat").alias("origin_airport_lat"), col("lon").alias("origin_airport_lon"), 
                 col("iata").alias("origin_airport_iata"), col("name").alias("origin_airport_name")]) \
        .join(airportsDF, col("dest_iata") == airportsDF.iata) \
        .withColumnRenamed("lat", "destination_airport_lat") \
        .withColumnRenamed("lon", "destination_airport_lon") \
        .withColumnRenamed("iata", "destination_airport_iata") \
        .withColumnRenamed("name", "destination_airport_name") \
        .drop(*('_id','country', 'icao', 'dest_iata', 'alt')) \
        .withColumn("port_distance", geodesic_udf(array("origin_airport_lat", "origin_airport_lon"), array("destination_airport_lat", "destination_airport_lon"))) \
    
    #fl.printSchema()
    
    fpzdf = fl.withColumn("timest",to_timestamp("ts")) \
                .withWatermark("timest", "30 seconds") \
                .groupBy(window("timest", "30 seconds", "15 seconds"), df["at_zone"]) \
                .avg("port_distance") \
                .withColumnRenamed("avg(port_distance)", "avgdistances")
    
    fpzdf.writeStream \
      .format("mongodb") \
      .option("checkpointLocation", "/tmp/mongocheckpoint3/") \
      .option("forceDeleteTempCheckpointLocation", "true") \
      .option("spark.mongodb.connection.uri", "mongodb://mongodb:27017/") \
      .option("spark.mongodb.database", "flightsDB") \
      .option("spark.mongodb.collection", "distancesRT") \
      .outputMode("append") \
      .start() \
      .awaitTermination()

    #fpzdf.writeStream \
    #  .format("console") \
    #  .outputMode("complete") \
    #  .start() \
    #  .awaitTermination()