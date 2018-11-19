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
Download the files to your local machine using git.  For example: git clone https://github.com/mstockwell/Check-VPC-IP-Address-Space.git

## Copy & Paste Deployement
Author a new Python 3.6 lambda function from Scratch.  Copy the code from LambdaCheckIPAvailableSpace\lambda_function.py into you new lambda and save. Set the timeout to 180 seconds. 
Add the following Environment Variables:

VPC_ID (Enter the VPC_ID of the VPC you wanted monitored.  If no VPC_ID is provided, the utility scans all subnets in all vpcs in all regions)

TARGET_ARN (The value will be the ARN of the SNS topic you create in the following step)

PERCENTAGE_WARNING (A number from 0 - 100 indicating remaining % of available IPs within a subnet.  For instance 20 means you want to be notified when a subnet only has 20% remaining IP addresses avaiable)

MESSAGE_SUBJECT (The Subject line of the message you wanted displayed (e.g. in email or txt message)

Create an SNS topic and update the TARGET_ARN environment variable with the SNS topic ARN. Subscribe to the topic.
Create a CloudWatch Schedule Event that triggers the Lambda function based on a rate you set, e.g. every 8 hours.
Create a role for Lambda with necessary permissions to describe regions, vpcs, subnets, and write to cloudwatch logs, and publish to SNS topic.

## SAM Deployment
At the command line, enter the following command and press return: (select an S3 bucket and name for your CloudFormation stack)
`aws cloudformation package --template-file template.yaml  --output-template-file output.yaml --s3-bucket <yourbucketname>  --s3-prefix <cloudformationstack>`  

The above command packages your lambda functions and puts them in your S3 bucket.  In addition, the SAM template will be transformed into a CloudFormation template to be used in the next step for creating your infrastructure stack.

Next, enter the following command and press return: aws cloudformation deploy --template-file output.yaml --stack-name <cloudformationstack> --capabilities CAPABILITY_NAMED_IAM

You should see Waiting for changeset to be created.. 
The above command creates the necessary AWS infrastructure including a lambda role, an SNS topic, and a CloudWatch Schedule Event.  
Deploying the infrastructure will take approximately 3 minutes.  Upon completion of the stack deployment, you will see the message, Successfully created/updated stack - <cloudformationstack>

Once deployed, you will need to enter a VPC_ID in the environment variable IF you want single VPC mode, otherwise the utility will scan all subnets, in all VPCs
in all Regions.  In addition, you will need to subscribe to the SNS topic named, 'IPAddressExahustion'.  You will also need to enable the Cloudwatch Schedule Event named,
'Lambda_Check_Available_IP_Addresses'.  The event runs every 8 hours.  You can edit the run rate to meet your needs.