from __future__ import print_function
import json
import boto3
import os
import ipaddress


ec2 = boto3.resource('ec2')
notify = boto3.client('sns')

vpc = ec2.Vpc(os.environ['VPC_ID'])
percent_warning = int(os.environ['PERCENTAGE_WARNING'])
target_arn = os.environ['TARGET_ARN']
subject = os.environ['MESSAGE_SUBJECT']

def compute_available_ips(subnet):
    print('Subnet: ',subnet.id)
    available_ips = subnet.available_ip_address_count
    print('Remaining IPs available: ', available_ips)
    total_ips = ipaddress.ip_network(subnet.cidr_block).num_addresses
    print('Total IPs in the subnet: ', total_ips)
    return round(available_ips/total_ips,2)*100
    
def lambda_handler(event, context):
    subnets = list(vpc.subnets.all())
    for subnet in subnets:
        percent_remaining = compute_available_ips(subnet)
        print ('percent_remaining: ', percent_remaining,'%')
        if percent_remaining <= percent_warning:
            message_txt = 'Subnet: ' + subnet.id + ' has only ' + str(percent_remaining) + '% remaining IP addresses available!' 
            notify.publish (
                TargetArn=target_arn,
                Subject=subject,
                Message=(message_txt)
            )
