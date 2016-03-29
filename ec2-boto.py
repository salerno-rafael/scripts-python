import boto3

def ec2Instances():
   ec2 = boto3.resource('ec2')
   instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
   return map(lambda inst: inst.id, instances)

print ec2Instances()
