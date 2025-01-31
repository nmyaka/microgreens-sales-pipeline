import json 
import boto3
import time

def lambda_handler(event, context):
    # Extract S3 bucket and object details
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    # Construct the full S3 path
    s3_path = f"s3://{bucket_name}/{object_key}"

    # Step Functions client
    stepfunctions = boto3.client('stepfunctions')

    # Step Functions ARN
    state_machine_arn = 'arn:aws:states:us-east-1:699475920597:stateMachine:MyStateMachine-bnqz5h0ky'

    # Generate a unique execution name based on object key and timestamp
    execution_name = f"microgreens-{object_key.replace('/', '-')}-{int(time.time())}"

    # Check if there are any running executions
    running_executions = stepfunctions.list_executions(
        stateMachineArn=state_machine_arn,
        statusFilter="RUNNING"
    )

    if running_executions['executions']:
        print("A Step Function execution is already running. Skipping duplicate execution.")
        return {
            "statusCode": 200,
            "body": json.dumps("Skipping duplicate execution because one is already running.")
        }

        # Start Step Function Execution
    response = stepfunctions.start_execution(
        stateMachineArn=state_machine_arn,
        name=execution_name,  # Ensures uniqueness to avoid retries
        input=json.dumps({
            "s3Path": s3_path
        })
    )

    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }
