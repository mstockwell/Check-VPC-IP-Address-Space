# A Lambda utility which checks remaining availiable IP addresses within VPC subnets

VPC subnets have a finite number of available ip addresses.  Through automation and some AWS services (e.g. Lambda accessing resources in a VPC, Fargate creating ENIs) 
your subnets may begin to experience IP exhaustion without you explicitly knowing so. This application allows you to set a threshold for notification when the remaining available IPs in a subnet reach a certain percentage.  
The default is 20% but this can be changed using the PERCENTAGE_WARNING environment variable.  

# Two Modes: Single VPC and All VPCs All Regions
There are two options for running this utility: single VPC and All Regions All VPCs.  If the environment Variable, VPC_ID is populated,
the utility will only check for subnets within the VPC idenfified by VPC_ID.  If VPC_ID is left blank or is missing, the utility will
check all subnets in all VPCs in all Regions.  As you can imagine, selecting this option will require the Lambda function to run for 2-3 minutes, or more
(based on intial tests).

# Two Options for Deployment: Copy & Paste Lambda or SAM
Download the files to your local machine using git.  For example:
https://github.com/mstockwell/Check-VPC-IP-Address-Space.git

## Copy & Paste Deployement

## SAM Deployment
At the command line, enter the following command and press return:
`aws cloudformation package --template-file template.yaml  --output-template-file output.yaml --s3-bucket <yourbucketname>  --s3-prefix <yourcloudformationname>`  

The above command packages your lambda functions and puts them in your S3 bucket.  In addition, the SAM template will be transformed into a CloudFormation template to be used in the next step for creating your infrastructure stack.

Next, enter the following command and press return: aws cloudformation deploy --template-file output.yaml --stack-name <yourcloudformationname> --capabilities CAPABILITY_NAMED_IAM

You should see Waiting for changeset to be created.. 
The above command creates the necessary AWS infrastructure including a lambda role, an SNS topic, and a CloudWatch Schedule Event.  
Deploying the infrastructure will take approximately 3 minutes.  Upon completion of the stack deployment, Successfully created/updated stack - Alexa-Workshop-App
