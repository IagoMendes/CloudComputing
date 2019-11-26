import boto3
import os
import time
from pprint import pprint
from botocore.exceptions import ClientError


NAME = 'Iago'

KEY_PAIR_NAME = NAME+"Key"
KEY_FILE_NAME_OHIO = KEY_PAIR_NAME+"Ohio.pem"
KEY_FILE_NAME_NORTHVIRGINIA = KEY_PAIR_NAME+"NorthVirginia.pem"

SECURITY_GROUP_NAME = NAME+"SecurityGroup"
MONGO_SECURITY_GROUP = NAME+"MongoSecurityGroup"

TARGET_GROUP_NAME = NAME+"TargetGroup"
LOAD_BALANCER_NAME = NAME+"LoadBalancer"

AUTOSCALING_GROUP = NAME+"AutoScaling"
LAUNCH_CONFIGURATION = NAME+"LaunchConfiguration"

UBUNTU18_OHIO = 'ami-0d5d9d301c853a04a'
UBUNTU18_NV = 'ami-04b9e92b5572fa0d1' 

MAX_INSTANCES = 1
MIN_INSTANCES = 1
MAX_INSTANCES_AS = 5

###############################################################################
# KEY PAIR
###############################################################################

def keyPair(client):
    try:
        res = client.describe_key_pairs(KeyNames=[KEY_PAIR_NAME])

        try:
            res = client.delete_key_pair(KeyName=KEY_PAIR_NAME)
        except ClientError as e:
            print(e)

    except ClientError as e:
        print(e)

    try:
        key = client.create_key_pair(KeyName=KEY_PAIR_NAME)
        
        return key

    except ClientError as e:
        print(e)

###############################################################################
# SECURITY GROUP
###############################################################################

def deleteSecurityGroup(client, name):
    try: 
        res = client.describe_security_groups(GroupNames=[name])
        try:
            time.sleep(30)
            res = client.delete_security_group(GroupName=name)
        except ClientError as e:
            print(e)

    except ClientError as e:
        print("No Security Group called {} here" .format(name))

def createSecurityGroup(client):
    try:
        response = client.describe_vpcs()
        vpcId = response["Vpcs"][0]["VpcId"]
        group = client.create_security_group(Description= "Cloud Final Project", GroupName=SECURITY_GROUP_NAME, VpcId=vpcId)

        try:
            response = client.authorize_security_group_ingress(GroupName=SECURITY_GROUP_NAME,
                        IpPermissions=[
                            {'IpProtocol': 'tcp', 
                                'FromPort': 8000, 
                                'ToPort': 8000,
                                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                            }]
                        )

        except ClientError as e:
            print(e)
    
    except ClientError as e:
        print(e)

def createSecurityGroup2(client):
    try:
        response = client.describe_vpcs()
        vpcId = response["Vpcs"][0]["VpcId"]
        group = client.create_security_group(Description= "Cloud Final Project", GroupName=SECURITY_GROUP_NAME, VpcId=vpcId)
    
    except ClientError as e:
        print(e)

def securityGroupMongoDB(client):

    try: 
        res = client.describe_security_groups(GroupNames=[MONGO_SECURITY_GROUP])
        try:
            res = client.delete_security_group(GroupName=MONGO_SECURITY_GROUP)
        except ClientError as e:
            print(e)

    except ClientError as e:
        print("No Security Group called {} here" .format(MONGO_SECURITY_GROUP))

    try:
        group = client.create_security_group(Description= "Cloud Final Project", GroupName=MONGO_SECURITY_GROUP)

        try:
            response = client.authorize_security_group_ingress(GroupName=MONGO_SECURITY_GROUP,
                        IpPermissions=[
                            {'IpProtocol': 'tcp', 
                                'FromPort': 27017, 
                                'ToPort': 27017,
                                'IpRanges': [{'CidrIp': '172.0.0.0/8'}] # Amazon IPs only, but temporary
                            }]
                        )
            

        except ClientError as e:
            print(e)
    
    except ClientError as e:
        print(e)

###############################################################################
# TERMINATE INSTANCES 
###############################################################################

def instanceTerminate(client):
    res = client.describe_instances()
    term = []

    count = 0

    for i in res['Reservations']:
        for j in i['Instances']:
            if j['KeyName'] == KEY_PAIR_NAME and j['State']['Name'] != 'terminated':
                count += 1
                term.append(j['InstanceId'])
    
    if count != 0:
        response = client.terminate_instances(InstanceIds=term)

        waiter = client.get_waiter('instance_terminated')
        waiter.wait(InstanceIds=term)

###############################################################################
# TARGET GROUP
###############################################################################

def deleteTargetGroup():
    try:
        res = elClientNv.describe_target_groups(
            Names=[TARGET_GROUP_NAME,
                ])
        arn = res["TargetGroups"][0]["TargetGroupArn"]
        delete = elClientNv.delete_target_group(TargetGroupArn=arn)

    except ClientError as e:
        print("No Launch Configuration called "+ TARGET_GROUP_NAME+", skipping.")

def createTargetGroup():
    vpc = clientNv.describe_vpcs()
    vpcId = vpc['Vpcs'][0]['VpcId']

    target = elClientNv.create_target_group(
        Name=TARGET_GROUP_NAME,
        Protocol='HTTP',
        Port=8000,
        VpcId=vpcId,
        HealthCheckProtocol='HTTP',
        HealthCheckPath='/healthcheck',
        TargetType='instance'
    )

    return target['TargetGroups'][0]['TargetGroupArn']

###############################################################################
# LOAD BALANCER
###############################################################################

def deleteLoadBalancer():
    try:
        arn = elClientNv.describe_load_balancers(Names=[LOAD_BALANCER_NAME])["LoadBalancers"][0]["LoadBalancerArn"]
        
        response = elClientNv.delete_load_balancer(LoadBalancerArn=arn)

        waiter = elClientNv.get_waiter('load_balancers_deleted')
        waiter.wait(LoadBalancerArns=[arn])
        time.sleep(60)

    except ClientError as e:
        print("No existing Load Balancer called "+ LOAD_BALANCER_NAME +", skipping.")

def createLoadBalancer():
    sc = clientNv.describe_security_groups(GroupNames=[SECURITY_GROUP_NAME])["SecurityGroups"][0]["GroupId"]
    
    lb = elClientNv.create_load_balancer(
        Name=LOAD_BALANCER_NAME,
        Subnets=[
            'subnet-e189c8ab',
            'subnet-c2a760fc',
            'subnet-82d868e5',
            'subnet-7e037471',
            'subnet-5287350e',
            'subnet-1965d937'
        ],
        SecurityGroups=[sc],
        Scheme='internet-facing',
        Type='application',
        IpAddressType='ipv4'
    )
    
    waiter = elClientNv.get_waiter('load_balancer_exists')
    waiter.wait(LoadBalancerArns=[ lb['LoadBalancers'][0]['LoadBalancerArn'] ])
    time.sleep(60)

    return lb['LoadBalancers'][0]['LoadBalancerArn']

###############################################################################
# LAUNCH CONFIGURATION
###############################################################################

def deleteLaunchConfiguration():
    try:
        autoClientNv.delete_launch_configuration(LaunchConfigurationName=LAUNCH_CONFIGURATION)
    except ClientError as e:
        print("No Launch Configuration called "+ LAUNCH_CONFIGURATION+", skipping.")

def createLaunchConfiguration(imageName, ip):
    data = '''#! /bin/bash
    sudo apt update -y
    sudo apt install git
    sudo apt install python3-pip -y
    sudo pip3 install requests -y
    sudo pip3 install fastapi
    sudo pip3 install uvicorn
    sudo pip3 install email-validator
    git clone https://github.com/IagoMendes/CloudComputing.git
    cd CloudComputing/Project
    export redirectIp={}
    uvicorn redirect:app --reload --host 0.0.0.0 &
    curl 127.0.0.1:8000''' .format(ip) 

    sc = autoClientNv.create_launch_configuration(
        LaunchConfigurationName=LAUNCH_CONFIGURATION,
        InstanceType='t2.micro', 
        KeyName=KEY_PAIR_NAME,
        InstanceMonitoring={'Enabled': True},
        SecurityGroups=[SECURITY_GROUP_NAME],
        UserData=data,
        ImageId=imageName)

###############################################################################
# AUTOSCALING
###############################################################################

def deleteAutoScaling():
    try:
        update = autoClientNv.update_auto_scaling_group(
            AutoScalingGroupName=AUTOSCALING_GROUP,
            MinSize=0,
            MaxSize=0,
            DesiredCapacity=0
        )

        delete = autoClientNv.delete_auto_scaling_group(
            AutoScalingGroupName=AUTOSCALING_GROUP,
            ForceDelete=True
        )

        while True:
            res = autoClientNv.describe_auto_scaling_groups(
                    AutoScalingGroupNames=[AUTOSCALING_GROUP]
                )
            if len(res['AutoScalingGroups']) == 0:
                break

    except ClientError as e:
        print("No Auto Scaling Group called {} here" .format(AUTOSCALING_GROUP))

def createAutoScaling(target):
    res = autoClientNv.create_auto_scaling_group(
            AutoScalingGroupName=AUTOSCALING_GROUP,
            MinSize=MIN_INSTANCES,
            MaxSize=MAX_INSTANCES_AS,
            DesiredCapacity=MIN_INSTANCES,
            LaunchConfigurationName=LAUNCH_CONFIGURATION,
            TargetGroupARNs=[target],
            AvailabilityZones=[
                'us-east-1a',
                'us-east-1b',
                'us-east-1c',
                'us-east-1d',
                'us-east-1e',
                'us-east-1f'
            ],
            Tags=[
                {
                    'Key'  : 'Owner',
                    'Value': NAME
                },
                {
                    'Key'  : 'Name',
                    'Value': NAME+'AutoScaling' 
                }]       
    )

###############################################################################
# CREATE INSTANCES 
###############################################################################

def instanceCommunicationCreate(client, resource, imageName, ip_ohio):
    data='''#! /bin/bash
    sudo apt update -y
    sudo apt install git
    sudo apt install python3-pip -y
    sudo pip3 install requests -y
    sudo pip3 install fastapi
    sudo pip3 install uvicorn
    sudo pip3 install email-validator
    git clone https://github.com/IagoMendes/CloudComputing.git
    cd CloudComputing/Project
    export redirectIp={}
    uvicorn redirect:app --reload --host 0.0.0.0 &
    curl 127.0.0.1:8000''' .format(ip_ohio) 

    inst = resource.create_instances(
            InstanceType='t2.micro', 
            KeyName=KEY_PAIR_NAME,
            MaxCount=MAX_INSTANCES, 
            MinCount=MIN_INSTANCES,
            SecurityGroups=[SECURITY_GROUP_NAME],
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key'  : 'Owner',
                            'Value': NAME
                        },
                        {
                            'Key'  : 'Name',
                            'Value': NAME+'Project' 
                        }
                        ]
                },
            ],
            UserData=data,
            ImageId=imageName)
    

    waiter = client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[inst[0].id])

    res = client.describe_instances()
    ret = []

    for i in res['Reservations']:
        for j in i['Instances']:
            if j['KeyName'] == KEY_PAIR_NAME and j['State']['Name'] != 'terminated':
                for tag in j['Tags']:
                    if tag['Value'] == NAME+"Project":
                        ret.append(j)
    
    ip = ret[0]['NetworkInterfaces'][0]['PrivateIpAddresses'][0]["Association"]['PublicIp']

    response = clientOhio.authorize_security_group_ingress(GroupName=SECURITY_GROUP_NAME,
                        IpPermissions=[
                            {'IpProtocol': 'tcp', 
                                'FromPort': 8000, 
                                'ToPort': 8000,
                                'IpRanges': [{'CidrIp': ip+'/32'}]
                            }]
                        )

    
    return ip

def instanceWebMongoCreate(client, resource, imageName, ip):
    data='''#! /bin/bash
    sudo apt update -y
    sudo apt install git
    sudo apt install python3-pip -y
    sudo pip3 install pymongo
    sudo pip3 install fastapi
    sudo pip3 install uvicorn
    sudo pip3 install email-validator
    git clone https://github.com/IagoMendes/CloudComputing.git
    cd CloudComputing/APS1
    export cloudDatabase={}
    uvicorn main2:app --reload --host 0.0.0.0 &
    curl 127.0.0.1:8000''' .format(ip) 

    inst = resource.create_instances(
            InstanceType='t2.micro', 
            KeyName=KEY_PAIR_NAME,
            MaxCount=MAX_INSTANCES, 
            MinCount=MIN_INSTANCES,
            SecurityGroups=[SECURITY_GROUP_NAME],
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key'  : 'Owner',
                            'Value': NAME
                        },
                        {
                            'Key'  : 'Name',
                            'Value': NAME+'Project' 
                        }
                        ]
                },
            ],
            UserData=data,
            ImageId=imageName)
    

    waiter = client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[inst[0].id])

    res = client.describe_instances()
    ret = []

    for i in res['Reservations']:
        for j in i['Instances']:
            if j['KeyName'] == KEY_PAIR_NAME and j['State']['Name'] != 'terminated':
                for tag in j['Tags']:
                    if tag['Value'] == NAME+"Project":
                        ret.append(j)
    
    ip = ret[0]['NetworkInterfaces'][0]['PrivateIpAddresses'][0]["Association"]['PublicIp']
    privateIp = ret[0]['NetworkInterfaces'][0]['PrivateIpAddresses'][0]["PrivateIpAddress"]

    response = clientOhio.authorize_security_group_ingress(GroupName=MONGO_SECURITY_GROUP,
                        IpPermissions=[
                            {'IpProtocol': 'tcp', 
                                'FromPort': 27017, 
                                'ToPort': 27017,
                                'IpRanges': [{'CidrIp': privateIp+'/32'}]
                            }]
                        )
    
    response = clientOhio.revoke_security_group_ingress(GroupName=MONGO_SECURITY_GROUP,
                        IpPermissions=[
                            {'IpProtocol': 'tcp', 
                                'FromPort': 27017, 
                                'ToPort': 27017,
                                'IpRanges': [{'CidrIp': '172.0.0.0/8'}]
                            }]
                        )

    return ip

def instanceMongoCreate(client, resource, imageName):
    inst = resource.create_instances(
            InstanceType='t2.micro', 
            KeyName=KEY_PAIR_NAME,
            MaxCount=1, 
            MinCount=1,
            SecurityGroups=[MONGO_SECURITY_GROUP],
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key'  : 'Owner',
                            'Value': NAME
                        },
                        {
                            'Key'  : 'Name',
                            'Value': NAME+'Mongo' 
                        }
                        ]
                },
            ],
            UserData='''#cloud-config
                    runcmd:
                    - sudo apt update -y
                    - sudo apt-get install gnupg
                    - wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -
                    - echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.2.list
                    - sudo apt-get update -y
                    - sudo apt-get install -y mongodb-org
                    - echo "mongodb-org hold" | sudo dpkg --set-selections
                    - echo "mongodb-org-server hold" | sudo dpkg --set-selections
                    - echo "mongodb-org-shell hold" | sudo dpkg --set-selections
                    - echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
                    - echo "mongodb-org-tools hold" | sudo dpkg --set-selections
                    - sudo service mongod start,
                    - sudo sed -i "s/127.0.0.1/0.0.0.0/g" /etc/mongod.conf
                    - sudo service mongod restart''',
            ImageId=imageName
            )
    

    waiter = client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[inst[0].id])

    res = clientOhio.describe_instances()
    ret = []

    for i in res['Reservations']:
        for j in i['Instances']:
            if j['KeyName'] == KEY_PAIR_NAME and j['State']['Name'] != 'terminated':
                for tag in j['Tags']:
                    if tag['Value'] == NAME+"Mongo":
                        ret.append(j)
    
    ip = ret[0]['NetworkInterfaces'][0]['PrivateIpAddresses'][0]["PrivateIpAddress"]
    return ip

###############################################################################
# LISTENER
###############################################################################

def createListener(tg, lb):
    response = elClientNv.create_listener(
            LoadBalancerArn = lb,
            Protocol='HTTP',
            Port=8000,
            DefaultActions=[
                {
                    'Type': 'forward',
                    'TargetGroupArn': tg
                }
            ])

###############################################################################
# MAIN
###############################################################################

def mainOhio(): # Working
    print("------------ Creating Ohio ------------\n")

    # Searches for existing instances created with specific keys
    print("Terminating existing instances.") 
    instanceTerminate(clientOhio)
    
    # Finds and deletes existing keypairs
    print("Creating Keypair and saving in "+KEY_PAIR_NAME+"Ohio.pem")
    key = keyPair(clientOhio)

    if KEY_FILE_NAME_OHIO in os.listdir():
        os.remove(KEY_FILE_NAME_OHIO)
            
    new_key = open(KEY_FILE_NAME_OHIO, "w")
    new_key.write(key['KeyMaterial'])
    new_key.close()
    os.chmod(KEY_FILE_NAME_OHIO, 0o400)

    # Creates security groups for regular webservers
    print("Deleting Security Group.")
    deleteSecurityGroup(clientOhio, SECURITY_GROUP_NAME)
    print("Creating Security Group.")
    createSecurityGroup2(clientOhio)

    # Creates security groups for the instance with Mongo
    print("Creating Mongo's Security Group.")
    securityGroupMongoDB(clientOhio)

    # Creating instances
    print("Creating Mongo instance in Ohio (us-east-2).")
    ip_mongo = instanceMongoCreate(clientOhio, resourceOhio, UBUNTU18_OHIO)

    print("Creating Ohio (us-east-2) Webserver linked to mongo ip: "+ip_mongo)
    ip = instanceWebMongoCreate(clientOhio, resourceOhio, UBUNTU18_OHIO, ip_mongo)
    return ip
    

def mainNorthVirginia(ip_ohio):
    print("\n \n------------ Creating North Virginia ------------\n")
  
    # Delete AutoScaling Group
    print("Deleting AutoScaling Group.")
    deleteAutoScaling()
    
    # Searches for existing instances created with specific keys 
    print("Terminating existing instances.")
    instanceTerminate(clientNv)
    
    # Delete Load Balancer
    print("Deleting Load Balancer.")
    deleteLoadBalancer() 
    
    # Delete Target Group
    print("Deleting Target Group.")
    deleteTargetGroup() 

    # Deletes Launch Configuration
    print("Deleting Launch Configuration.")
    deleteLaunchConfiguration()

    # Finds and deletes existing keypairs
    print("Creating Keypair and saving in "+KEY_PAIR_NAME+"NorthVirginia.pem")
    key = keyPair(clientNv)

    if KEY_FILE_NAME_NORTHVIRGINIA in os.listdir():
        os.remove(KEY_FILE_NAME_NORTHVIRGINIA)
            
    new_key = open(KEY_FILE_NAME_NORTHVIRGINIA,"w")
    new_key.write(key['KeyMaterial'])
    new_key.close()
    os.chmod(KEY_FILE_NAME_NORTHVIRGINIA, 0o400)

    # Deletes Security Group
    print("Deleting Security Group.")
    deleteSecurityGroup(clientNv, SECURITY_GROUP_NAME)

    # Creates security groups for regular webservers
    print("Creating new Security Group.")
    createSecurityGroup(clientNv)

    # Creates Communication Instance
    print("Creating instance to communicate to Ohio Webserver ip: {}" .format(ip_ohio))
    ip_communication = instanceCommunicationCreate(clientNv, resourceNv, UBUNTU18_NV, ip_ohio)

    # Creates Load Balancer
    print("Creating Load Balancer.")
    loadBalancerARN = createLoadBalancer() 

    # Creates Target Group
    print("Creating Target Group.")
    targetGroupARN = createTargetGroup()

    # Creates Listener
    print("Creating Listener.")
    createListener(targetGroupARN, loadBalancerARN)

    # Creates Launch Configuration
    print("Creating Launch Configuration.")
    createLaunchConfiguration(UBUNTU18_NV, ip_communication)

    # Creates AutoScaling
    print("Creating AutoScaling Group.")
    createAutoScaling(targetGroupARN)
    


if __name__ == "__main__":
    clientOhio = boto3.client('ec2', region_name='us-east-2')
    resourceOhio = boto3.resource('ec2', region_name='us-east-2')

    clientNv = boto3.client('ec2', region_name='us-east-1')
    resourceNv = boto3.resource('ec2', region_name='us-east-1')
    elClientNv = boto3.client('elbv2', region_name='us-east-1')
    autoClientNv = boto3.client('autoscaling', region_name='us-east-1')
    
    ip_ohio = mainOhio() 
    mainNorthVirginia(ip_ohio)