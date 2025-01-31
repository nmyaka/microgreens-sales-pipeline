# Microgreens Data Pipeline

## Overview
This project implements an automated data pipeline for processing microgreens sales data. The pipeline is triggered by an S3 event and executes various AWS services, including Lambda, Step Functions, Glue ETL, Glue Crawler, Athena, and SNS.

## Architecture
1. **S3 PUT Event**: Uploading a raw CSV file to an S3 bucket triggers the Lambda function.
2. **AWS Lambda**: Extracts bucket and file key details and starts the Step Functions workflow.
3. **AWS Step Functions**: Orchestrates the data processing steps:
   - **Glue ETL Job**: Cleans and processes the raw data and stores the processed data in S3.
   - **Glue Crawler**: Updates the AWS Glue Data Catalog.
   - **Get Crawler Info**: Retrieves database details needed to run Athena query.
   - **Get Table Info**: Fetches table details to run athena query.
   - **Athena Query Execution**: Runs SQL queries for data analysis and stores the query results back in S3.
   - **SNS Notification**: Sends a notification(Email) upon successful pipeline completion.

## Project Structure
```
 microgreens-data-pipeline/
 ├── lambda/
 │   ├── lambda_function.py  # Lambda function code
 ├── glue/
 │   ├── glue_etl_job.py     # Glue ETL Job script
 ├── step-functions/
 │   ├── state_machine.json  # Step Functions JSON definition
 ├── docs/
 │   ├── README.md           # Project documentation
 │   ├── sample_microgreens_sales_rawdata.csv
 │   ├── sample_athena_query_result.csv
 ├── .gitignore
 ├── requirements.txt        # Python dependencies
 ├── LICENSE                 # License file (optional)
```

## Setup Instructions
### Create an input/raw data S3 Bucket with an event notification added to trigger Lambda function

### Deploy AWS Lambda Function
- `invoke_step_functions.py` upload it to an AWS Lambda function.
- Attach necessary IAM permissions for triggering Step Functions.

### Set Up Glue ETL Job
- Upload `microgreens_etl_job.py` as a Glue ETL job.   
- Configure it to accept `raw_s3_path` as a parameter.

### Create and Configure Glue Crawler
- Create a Database and set up a Glue Crawler named microgreens-sales-crawler to update the Data Catalog.

### Create S3 Buckets for Athena
- Athena requires an S3 bucket to store query results. 
          "OutputLocation": "s3://microgreens-pipeline-output-bucket/athena-query-results/"

### Create SNS Topic
- Create SNS Topic and a subscription (Email) to be notified when the pipeline is complete. Use the Topic arn in the state_machine.json

### Create and Deploy Step Functions State Machine
- Use `state_machine.json` to create an AWS Step Functions workflow.
- Ensure it has permissions to invoke Glue, Athena, and SNS.

### Run the Pipeline
- Upload a CSV file to the input S3 bucket and monitor execution via Step Functions.

## Security Considerations
- **IAM Roles**: Ensure least privilege access for S3, Lambda, Glue, Athena, Step Functions and SNS.
- **Logging & Monitoring**: Enable AWS CloudWatch logs for debugging.

## Future Enhancements
- Add data validation and schema enforcement.
- Implement error handling and retries for failed steps.
- Optimize Glue ETL for better performance.

## License
This is a personal project.
