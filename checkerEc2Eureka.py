import boto3
import urllib2
import xml.etree.ElementTree as ET
from json import JSONEncoder
import BaseHTTPServer
import time
import sys
from functools import partial


EUREKA_NODE = "http://0.0.0.0:8080/v2/apps/EUREKA"
showText = lambda node : node.text
ec2 = boto3.resource('ec2')

class Instance(object):
        def __init__(self, instance, status):
                self.instance = instance
                self.status = status

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
	
def eurekaNodes():
        eurekaMetadata = urllib2.urlopen(EUREKA_NODE).read()
        root = ET.fromstring(eurekaMetadata)
        return map(showText, root.findall('.//hostName'))

def app (node):
        result = urllib2.urlopen("http://" + node + ":8080/v2/apps").read()
        root = ET.fromstring(result)
        return map(lambda inst: Instance(inst.find('dataCenterInfo/metadata/instance-id'),inst.find('status')),root.findall('./application/instance'))
        
def upElement(element):
    if element.status.text == 'UP':return True

def mergedNodes(nodes):
       merge = set()
       for node in nodes:
           for n in node:
               if upElement(n):
                   merge.add(n.instance.text)          
       return merge

def instancesEureka ():
     nodes = eurekaNodes()
     nodes.remove('ip-172-30-143-123')
     return nodes

def mergeInstanceEureka():
    nodes = mergedNodes(map(app,instancesEureka()))
    nodes = filter(lambda x: '10.' not in x,nodes)
    return nodes

def compareInstances(nodesEureka,ec2List1, ec2List2):
	count =  filter(lambda x: x in ec2List1 or x in ec2List2 ,nodesEureka)
    return len(count)

def compareInstancesRunnning(nodesEureka,ec2List):
    count = map(lambda x: filter(lambda y: x in y ,ec2List),nodesEureka)
    return len(count)

if __name__ == '__main__':
	nodesEureka = mergeInstanceEureka()
	if compareInstancesRunnning(nodesEureka,ec2Running()) == len(nodesEureka): exit(0)
	if compareInstances(nodesEureka,ec2Stoped(),ec2Terminated()) > 0 : exit(1)
	if compareInstances(nodesEureka,ec2Stoping(),ec2Terminating())> 0 : exit(2)
   

     

