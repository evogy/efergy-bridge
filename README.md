# AWS Lambda driver for Efergy meters

This Serverless project deployes three distinct Lambda functions:

- **authorizerUser** This function enable the authorizer capabilities of API Gateway. It queries the DynamoDB table to check if the API token in the http header request is valid or not.
- **worker** This function polls the [Efergy] cloud platform to retrive the data for each plant added
- **webapi** This function is a Flask application that make available the following API endpoints:
    - **[GET] /plants** Return all the available plants
    - **[GET] /plants/{id}** Return a particular plant
    - **[POST] /plants** Create a new plant. The accepted body is  
        ```
            {
                "api_key": Required,
                "plant_id": Required,
                "name": Required
            }
        ```
    - **[PUT] /plants/{id}** Update a particular plant
    - **[DELETE] /plants/{id}** Delete a particular plant

[Efergy]:http://efergy.com/

## Configuration

1. Set-up one environment variables:
    - AWS_PROFILE: the AWS CLI profile
2. Set-up the following  **secured** variables in the AWS Parameter store:
    - **RABBIT_USER** The rabbitmq username
    - **RABBIT_PASS** The rabbitmq password
    - **RABBIT_HOST** The rabbitmq hostname
3. Use `sls plugin install -n serverless-python-requirements` to install the requirements.txt serverless plugin.
4. Use `sls plugin install serverless-wsgi` to install the wsgi engine for the API endpoint management
5. Install and configure the AWS Lambda Layer by cloning [this repo] and following the instructions reported. Copy the ARN of the Lambda function in the **layers** section of the serverless.yml file:

    **N.B** This is required to enable the API call caching function.

4. Run `sls deploy` 

[this repo]:https://github.com/evogy/sqlite-lambda-layer/tree/master

To test on local pc you have to:

1. Execute the DynamoDb dockerized local version with:
`docker run -it -p 8000:8000 amazon/dynamodb-local -jar DynamoDBLocal.jar -sharedDb`

2. Execute the Wsgi server:
`sls wsgi serve`

3. To test the `worker` and `authorizerUser`functions, run:

    `sls invoke local -f worker`


