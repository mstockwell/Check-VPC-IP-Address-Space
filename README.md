# A Lambda utility which checks remaining availiable IP addresses within VPC subnets

Subnets have a finite number of available ip addresses.  Through automation and some AWS services, such as Lambda accessing resources in a VPC and Fargate Tasks.

This application allows you to set a threshold for notification when the remaining available IPs in a subnet reach a certain percentage.  The default is 20%.  


## Download project source code and templates

Code and infrastructure templates for this workshop are securely stored in AWS CodeCommit.  CodeCommit is a fully-managed source control service that makes it easy for companies to host secure and highly scalable private Git repositories. CodeCommit eliminates the need to operate your own source control system or worry about scaling its infrastructure. You can use CodeCommit to securely store anything from source code to binaries, and it works seamlessly with your existing Git tools.

Within the Cloud9 Terminal window, enter the following command:

`git clone https://github.com/mstockwell/Alexa-Serverless-Comprehend-Workshop.git`  This process, which should take less than a minute, will download and clone the repo to your Cloud9 environment.

Next, we will change the working directory to the local git repository you just cloned in your Cloud9 environment.  Within the Terminal window, type the following and hit return: `cd Alexa-Serverless-Comprehend-Workshop`

## Create an S3 bucket to store and deploy AWS Lambda functions 

S3 is AWS’ object storage service.  We will automatically be implementing most of the infrastructure and code using two AWS services, CloudFormation and SAM, described in detail later in the document.  SAM requires Lambda code to be stored in S3 so that CloudFormation can access it to deploy your lambda functions when it builds out infrastructure in AWS.  We will be creating your S3 bucket via the AWS command line.  

S3 buckets must be globally unique across all customers.  Therefore, a script has been created that will uniquely name and create your S3 bucket.  Confirm you are still in the *Alexa-Serverless-Comprehend-Workshop* directory and execute the following command in the Cloud9 terminal window: `. createbucket.sh` **(Don’t forget the leading period)**

In response, you will see *make_bucket:* followed by the unique name of your S3 bucket.  Go back to the AWS Console and select the S3 service, making sure you are in the US-East Region.  You will see your new S3 bucket listed in the console.


## Create AWS infrastructure and deploy Lambda functions

AWS CloudFormation provides a common language to describe and provision all the infrastructure resources in your cloud environment. CloudFormation allows you to use a simple text file to model and provision, in an automated and secure manner, all the resources needed for your applications across all regions and accounts. This file serves as the single source of truth for your cloud environment. 

The AWS Serverless Application Model (SAM) is a model to define serverless applications. SAM is natively supported by AWS CloudFormation and defines simplified syntax for expressing serverless resources.

### Run SAM and CloudFormation to create initial infrastructure and code
At the command line, enter the following command and press return:
`aws cloudformation package --template-file template.yaml  --output-template-file output.yaml --s3-bucket <yourbucketname>  --s3-prefix <yourcloudformationname>`  

The above command packages your lambda functions and puts them in your S3 bucket.  In addition, the SAM template will be transformed into a CloudFormation template to be used in the next step for creating your infrastructure stack.