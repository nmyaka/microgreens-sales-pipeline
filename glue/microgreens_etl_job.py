import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from awsglue.transforms import *
from pyspark.sql.functions import col
import numpy as np

# Initialize Glue Context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Read S3 path from Step Functions arguments
args = sys.argv
raw_s3_path = args[args.index("--raw_s3_path") + 1] if "--raw_s3_path" in args else "s3://microgreens-pipeline-input-bucket/"

# Read raw CSV data from S3 dynamically
raw_df = glueContext.create_dynamic_frame.from_options(
    format_options={"withHeader": True, "separator": ","},
    connection_type="s3",
    format="csv",
    connection_options={"paths": [raw_s3_path], "recurse": True}
)
# Convert DynamicFrame to DataFrame for processing
dataframe = raw_df.toDF()

# Coalesce to a single partition
dataframe = dataframe.coalesce(1)

# Data Cleaning Transformations

# Replace empty strings with NaN
dataframe = dataframe.na.replace("", None)

# Handle missing values (e.g., fill with default values)
dataframe = dataframe.fillna({"unitprice": 0, "city": "unknown", "size": "unknown"})

# Filter out invalid records (e.g., negative prices)
lower_bound = 3 # Minimum price
upper_bound = 9 # Maximum price

# Ensure 'unitprice' column is of type float
dataframe = dataframe.withColumn("unitprice", col("unitprice").cast("float"))

# Apply filtering conditions
cleaned_dataframe = dataframe.filter(
    (col("unitprice").isNotNull()) & 
    (col("city").isNotNull()) & 
    (col("size").isNotNull()) & 
    (col("unitprice") >= lower_bound) & 
    (col("unitprice") <= upper_bound)
)

# Drop duplicate records
valid_records_dataframe = cleaned_dataframe.drop_duplicates()

# Rename columns if needed
#renamed_frame = valid_records_dataframe.rename_field("unitprice", "unitPrice")

# Convert DataFrame back to DynamicFrame
output_dynamic_frame = DynamicFrame.fromDF(valid_records_dataframe, glueContext, "output_dynamic_frame")

# Write cleaned data back to S3
output_path = "s3://microgreens-pipeline-output-bucket/processed-data/"
glueContext.write_dynamic_frame.from_options(
    frame=output_dynamic_frame,
    connection_type="s3",
    connection_options={"path": output_path},
    format="csv"
)

job.commit()
