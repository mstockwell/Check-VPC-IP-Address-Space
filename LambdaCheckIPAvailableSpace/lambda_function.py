import boto3
import os
import ipaddress

percent_warning = int(os.environ['PERCENTAGE_WARNING'])
target_arn = os.environ['TARGET_ARN']
subject = os.environ['MESSAGE_SUBJECT']
message_txt = ''

def compute_available_ips(subnet):
    available_ips = subnet.available_ip_address_count
    total_ips = ipaddress.ip_network(subnet.cidr_block).num_addresses
    return round(available_ips/total_ips,2)*100
    
def determine_notification(percent_remaining, region, vpc, subnet):
    if percent_remaining <= percent_warning:
        global message_txt
        message_txt += 'Subnet: ' + subnet + ' in VPC ' + vpc + \
                    ' in Region ' + region + ' has ' + str(percent_remaining) \
                    + '% remaining IP addresses available...' +'\r'
                    
def lambda_handler(event, context):
    global message_txt
    if 'VPC_ID' not in os.environ or os.environ['VPC_ID'] == '' :
        region_client = boto3.client('ec2')
        regions = region_client.describe_regions()
        for region in regions['Regions']:
            vpc_client = boto3.client('ec2', region_name=region['RegionName'])
            vpcs = vpc_client.describe_vpcs()
            for vpc in vpcs['Vpcs']:
                vpc_resource = boto3.resource('ec2',region_name=region['RegionName'])
                vpc_object = vpc_resource.Vpc(vpc['VpcId'])
                subnets = list(vpc_object.subnets.all())
                for subnet in subnets:
                    percent_remaining = compute_available_ips(subnet)
                    determine_notification(percent_remaining, region['RegionName'], vpc_object.vpc_id, subnet.subnet_id)
    else:
        if 'REGION_ID' not in os.environ or os.environ['REGION_ID'] == '':
            region_id = os.environ['AWS_REGION']
        else:
            region_id = os.environ['REGION_ID']
        ec2 = boto3.resource('ec2',region_name=region_id)
        vpc = ec2.Vpc(os.environ['VPC_ID'])
        subnets = list(vpc.subnets.all())
        for subnet in subnets:
            percent_remaining = compute_available_ips(subnet)
            determine_notification(percent_remaining, region_id, vpc.vpc_id, subnet.subnet_id)
    
    if message_txt:
        notify = boto3.client('sns')
        notify.publish (
        TargetArn=target_arn,
        Subject=subject,
        Message=(message_txt)
        )
