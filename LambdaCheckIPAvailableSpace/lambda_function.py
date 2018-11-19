from __future__ import print_function
import json
import boto3
import os
import ipaddress

ec2 = boto3.resource('ec2')
notify = boto3.client('sns')

def compute_available_ips(subnet):
    available_ips = subnet.available_ip_address_count
    total_ips = ipaddress.ip_network(subnet.cidr_block).num_addresses
    return round(available_ips/total_ips,2)*100
    
def lambda_handler(event, context):
    percent_warning = int(os.environ['PERCENTAGE_WARNING'])
    target_arn = os.environ['TARGET_ARN']
    subject = os.environ['MESSAGE_SUBJECT']
    vpc = ec2.Vpc(os.environ['VPC_ID'])
    
    if not vpc.vpc_id:
        print ('No VPC')
    else:
        subnets = list(vpc.subnets.all())
        message_txt = ''
        for subnet in subnets:
            percent_remaining = compute_available_ips(subnet)
            if percent_remaining <= percent_warning:
                message_txt += 'Subnet: ' + subnet.id + ' has ' + str(percent_remaining) \
                + '% remaining IP addresses available...' +'\r'
        if message_txt:
            notify.publish (
            TargetArn=target_arn,
            Subject=subject,
            Message=(message_txt)
            )
