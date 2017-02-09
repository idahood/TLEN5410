#!/usr/bin/env python

import boto3
from datetime import datetime
from datetime import timedelta
from pprint import pprint

def get_instances(ec2):
    running_instances = []
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        running_instances.append(instance.id)
    return sorted(running_instances)

def get_statistic(client, metric_name, metric_unit, statistic, instance_id):
    result = client.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName=metric_name,
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=datetime.utcnow() - timedelta(minutes=30),
        EndTime=datetime.utcnow() + timedelta(minutes=10),
        Period=3600,
        Statistics=[statistic],
        Unit=metric_unit
        )

    return str(result['Datapoints'][0][statistic])

def main():
    ec2 = boto3.resource('ec2')
    client = boto3.client('cloudwatch')

    running_instances = get_instances(ec2)

    now = datetime.utcnow()
    past = now - timedelta(minutes=30)
    future = now + timedelta(minutes=10)

    for instance_id in running_instances:
        print "Instance ID: " + instance_id
        print "Status Check: " + get_statistic(client, 'StatusCheckFailed', 'Count', 'Maximum', instance_id)
        print "CPU Utilization: " + get_statistic(client, 'CPUUtilization', 'Percent', 'Average', instance_id)
        print "Network In: " + get_statistic(client, 'NetworkIn', 'Bytes', 'Average', instance_id)
        print "Network Out: " + get_statistic(client, 'NetworkOut', 'Bytes', 'Average', instance_id)

if __name__ == "__main__":
    main()
