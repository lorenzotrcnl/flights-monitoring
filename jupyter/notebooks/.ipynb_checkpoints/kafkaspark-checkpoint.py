from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType
from pyspark.sql.functions import from_json, col, to_timestamp, window

def write_and_info(df, batch_id):
    print("batch_id: {0}, # rows: {1}".format(batch_id, df.count()))

if __name__ == '__main__':
    spark = SparkSession.builder \
        .appName("kafkastream") \
        .master('local') \
        .config("spark.jars", "org.mongodb.spark_mongo-spark-connector-10.0.5.jar") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    
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
    
    finaldf = df.withColumn("timest",to_timestamp("ts")) \
                .withWatermark("timest", "60 seconds") \
                .groupBy(window("timest", "60 seconds", "30 seconds"), df["at_zone"]) \
                .avg("ground_speed") \
                .withColumnRenamed("avg(ground_speed)", "avgspeed")
    
    finaldf.writeStream \
      .format("mongodb") \
      .option("checkpointLocation", "/tmp/mongocheckpoint/") \
      .option("forceDeleteTempCheckpointLocation", "true") \
      .option("spark.mongodb.connection.uri", "mongodb://mongodb:27017/") \
      .option("spark.mongodb.database", "flightsDB") \
      .option("spark.mongodb.collection", "realtimecoll") \
      .outputMode("append") \
      .start() \
      .awaitTermination()

    #finaldf.writeStream \
    #  .format("console") \
    #  .outputMode("complete") \
    #  .start() \
    #  .awaitTermination()