import urllib2
import xml.etree.ElementTree as ET
from json import JSONEncoder
import BaseHTTPServer
import time
from functools import partial

EUREKA_NODE = "http://0.0.0.1:8080/v2/apps/EUREKA"

authFilter = lambda appName, appToFilterBy : appName == appToFilterBy
showText = lambda node : node.text

def eurekaNodes():
        eurekaMetadata = urllib2.urlopen(EUREKA_NODE).read()
        root = ET.fromstring(eurekaMetadata)
        return map(showText, root.findall('.//hostName'))

class Application(object):
        def __init__(self, nameAndHost, eurekaNode):
                self.nameAndHost = nameAndHost
                self.eurekaNode = eurekaNode

        def __str__(self):
                return "\n" + self.eurekaNode  + "\n" + "==============================" + "\n" + str(self.nameAndHost)

def app (node):
        result = urllib2.urlopen("http://" + node + ":8080/v2/apps").read()
        root = ET.fromstring(result)
        apps = map(showText, root.findall('./application/instance/app'))
        hostnames = map(showText, root.findall('./application/instance/hostName'))
        status = map(showText, root.findall('./application/instance/status'))
        instanceId = map(showText, root.findall('./application/instance/dataCenterInfo/metadata/instance-id'))
        print Application(zip(apps,status, instanceId), node)
        return  Application(zip(apps,status, instanceId), node)

if __name__ == '__main__':
        nodes = eurekaNodes()
        nodes.remove('ip-0-0-0-2')
        map(app, nodes)
~
