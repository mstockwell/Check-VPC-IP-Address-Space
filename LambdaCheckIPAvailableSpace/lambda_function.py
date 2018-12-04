from __future__ import print_function
import boto3
import os
import ipaddress

percent_warning = int(os.environ['PERCENTAGE_WARNING'])
target_arn = os.environ['TARGET_ARN']
subject = os.environ['MESSAGE_SUBJECT']
reclaim_enis = os.environ['RECLAIM_ENIS'].upper()

def check_for_low_ips (subnets, vpc, region):
    subnets_with_low_ips =[]    
    for subnet in subnets:
        available_ips = subnet.available_ip_address_count
        total_ips = ipaddress.ip_network(subnet.cidr_block).num_addresses
        percent_remaining = round(available_ips/total_ips,2)*100
        if percent_remaining <= percent_warning:
            subnets_with_low_ips.append([subnet.id,vpc,region,percent_remaining])
            if reclaim_enis == 'TRUE':
                network_interfaces = subnet.network_interfaces.all()
                for network_interface in network_interfaces:
                    if network_interface.status == 'available':
                        network_interface.delete()
                        print('ENI {} in VPC {} in Region {} has been reclaimed.'.format(network_interface.id,vpc,region))
    return (subnets_with_low_ips)

def send_notification(subnets_flagged):
    message_txt = ''
    for subnet in subnets_flagged:
        message_txt += 'Subnet: {} in VPC {} in Region {} has {}% remaining IP addresses available!'.format(subnet[0],subnet[1],subnet[2],subnet[3])
    notify = boto3.client('sns')
    notify.publish (
    TargetArn=target_arn,
    Subject=subject,
    Message=(message_txt)
    )
        
def lambda_handler(event, context):
    subnets_flagged = []
    if 'VPC_ID' not in os.environ or os.environ['VPC_ID'] == '' :
        region_client = boto3.client('ec2')
        regions = region_client.describe_regions()
        for region in regions['Regions']:
            vpc_client = boto3.client('ec2', region_name=region['RegionName'])
            vpcs = vpc_client.describe_vpcs()
            for vpc in vpcs['Vpcs']:
                vpc_resource = boto3.resource('ec2',region_name=region['RegionName'])
                vpc_object = vpc_resource.Vpc(vpc['VpcId'])
                low_ips = check_for_low_ips (list(vpc_object.subnets.all()), vpc_object.vpc_id, region['RegionName'])
                if low_ips: subnets_flagged.extend(low_ips)
    else:
        if 'REGION_ID' not in os.environ or os.environ['REGION_ID'] == '':
            region_id = os.environ['AWS_REGION']
        else:
            region_id = os.environ['REGION_ID']
        vpc_client = boto3.resource('ec2',region_name=region_id)
        vpc = vpc_client.Vpc(os.environ['VPC_ID'])
        subnets_flagged = check_for_low_ips(list(vpc.subnets.all()), vpc.vpc_id, region_id)
    if subnets_flagged:
        send_notification(subnets_flagged)
        