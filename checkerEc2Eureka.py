import boto3
import urllib2
import xml.etree.ElementTree as ET
from json import JSONEncoder
import BaseHTTPServer
import time
import sys
import itertools
from functools import partial

eureka_url = "http://localhost:8080/v2/apps/EUREKA"
showText = lambda node : node.text
ec2 = boto3.resource('ec2')

class Instance(object):
        def __init__(self, instance, status):
                self.instance = instance
                self.status = status

def eurekaNodes():
	 eurekaMetadata = urllib2.urlopen(eureka_url).read()
	 root = ET.fromstring(eurekaMetadata)
	 return map(showText, root.findall('.//hostName'))

def app (node):
        result = urllib2.urlopen("http://" + node + ":8080/v2/apps").read()
        root = ET.fromstring(result)
        return map(lambda inst: Instance(inst.find('dataCenterInfo/metadata/instance-id'),inst.find('status')),root.findall('./application/instance'))
        
def instancesEureka ():
     nodes = eurekaNodes()
     nodes.remove('ip-0-0-0-123')
     return nodes

def printMessage(node,msg):
	for n in node:print n +" - "+msg

def allInstanceEureka():
	return map(app,instancesEureka())

def mergeAllInstanceEureka(nodes):
	return list(itertools.chain(*nodes))

def instanceEurekaRunning(nodes):
	return filter(lambda x: x.status.text == 'UP',nodes)	

def instancesEurekaUnique(nodes):
	return set(map(lambda x: x.instance.text, nodes))

def ec2Running():
	return map(lambda x: x.id ,ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]))

def ec2Stoped():
	return map(lambda x: x.id ,ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]))

def ec2Stoping():
	return map(lambda x: x.id ,ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['stopping']}]))	

def ec2Terminated():
	return map(lambda x: x.id ,ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['terminated']}]))

def ec2Terminating():
	return map(lambda x: x.id ,ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['terminating']}]))			

def ec2AllInstances():
	return map(lambda x: Instance(x.id ,x.state),ec2.instances.all())

def compareInstances(nodesEureka,ec2List1, ec2List2):
	return filter(lambda x: x in ec2List1 or x in ec2List2 ,nodesEureka) 

def compareInstancesRunnning(nodesEureka,ec2List):
    return map(lambda x: filter(lambda y: x in y ,ec2List),nodesEureka) 

def ckeckCritical(nodesEureka):
	instances = compareInstances(nodesEureka,ec2Stoped(),ec2Terminated())
	if len(instances) > 0 : 
		printMessage(instances,'instance-id status Stopped/Terminated in AWS but OK status in EUREKA')
		exit(2)

def ckeckWarnning(nodesEureka):
	instances = compareInstances(nodesEureka,ec2Stoping(),ec2Terminating())
	if len(instances) > 0 : 
		printMessage(instances,'instance-id status Stopping/Terminating in AWS but OK status in EUREKA')
		exit(1)

def ckeckRunning(nodesEureka):
	instances = compareInstancesRunnning(nodesEureka,ec2Running())
	if len(instances) == len(nodesEureka):
		print 'instances running/ok'
		exit(0)	

if __name__ == '__main__':	
	nodesEureka = instancesEurekaUnique(
		instanceEurekaRunning(
			mergeAllInstanceEureka(
				allInstanceEureka())))
	
	ckeckCritical(nodesEureka)
	ckeckWarnning(nodesEureka)
	ckeckRunning(nodesEureka)
