#!/usr/bin/env python

import boto3

def display_instances(ec2):
    '''
        Display all instances with state of running or stopped
    '''
    instances = ec2.instances.filter()
    for instance in instances:
        print(instance.id, instance.instance_type, instance.public_ip_address, instance.state['Name'])

def launch_instance(ec2, ami, inst):
    '''
        Start new instance with ami
    '''
    ec2.create_instances(ImageId=ami, InstanceType=inst, MinCount=1, MaxCount=2)

def stop_instance(ec2, instance_id):
    '''
        Stop a specfic instance
    '''
    ec2.instances.filter(InstanceIds=[instance_id]).stop()

def get_newest(ec2):
    '''
        Iterate through all instances, return Instance with lowest launc_time
    '''

    instance_list = []
    instances = ec2.instances.filter()
    for instance in instances:
        instance_list.append( (instance.launch_time, instance.id) )
    return sorted(instance_list)[0]

def main():
    AMI_UBUNTU = 'ami-7c803d1c'
    INST_T2_MICRO = 't2.micro'

    ec2 = boto3.resource('ec2')

    instances = ec2.instances.filter()
    num_instances = 0
    for i in instances:
        num_instances += 1

    if num_instances < 4:
        #launch two instances
        launch_instance(ec2, AMI_UBUNTU, INST_T2_MICRO)

        #grab youngest instance id
        youngest_start, youngest_id = get_newest(ec2)

        #shut down newest
        stop_instance(ec2, youngest_id)

    display_instances(ec2)

if __name__ == "__main__":
    main()
