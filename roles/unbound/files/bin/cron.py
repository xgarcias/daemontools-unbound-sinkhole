#!/usr/local/bin/python

import urllib2
import sys
import re
import subprocess
import time



config_dir="/usr/local/var/service/unbound/config/"
config_file="/usr/local/var/service/unbound/unbound.conf"
control_cmd="/usr/local/sbin/unbound-control -c /usr/local/var/service/unbound/unbound.conf"

def load_urls():
    urls=[]
    try:
        fd=open("%s/lists.txt" % config_dir)
        for line in fd.readlines():
            urls.append(line.strip())
        fd.close()
    
    except Exception, e:
        print "Unable to load urls: %s " % (e)
        sys.exit(1)

    return urls

def download_list(url):
    record=[]
    try:
        fd = urllib2.urlopen(url)
        for line in fd.readlines():
            if re.search("^#|^$|^Site",line) == None:
                record.append(line.strip())
        fd.close()
    except Exception, e:
        print "error downloading url %s : %s " % (url,e)
        sys.exit(1)
    return record


blacklist=[]

def dump_cache():
    p=subprocess.Popen("%s dump_cache" % control_cmd,
                            shell=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            )
    stdout,stderr = p.communicate()
    fd=open("%s/cache.txt" % config_dir, 'w')
    fd.write(stdout)
    fd.close()

def load_cache():
    fd=open("%s/cache.txt" % config_dir)
    p=subprocess.Popen("%s -q  load_cache" % control_cmd,
                            shell=True,
                            stdin=fd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            )
    stdout,stderr = p.communicate()

def reload_service():
    p=subprocess.Popen("%s -q  reload" % control_cmd,
                            shell=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            )
    stdout,stderr = p.communicate()

def check_service():
    p=subprocess.Popen("/usr/local/sbin/unbound-checkconf %s" % config_file,
                            shell=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            )
    stdout,stderr = p.communicate()
    return p.returncode


dump_cache()

for url in load_urls():
    blacklist = blacklist + download_list(url)


try:
    fd=open("%s/blackhole.zone" % config_dir, "w")
    for line in  set(blacklist):
        fd.write("local-zone: '%s' redirect\n" % line.strip())
        fd.write("local-data: '%s IN A 127.0.0.1'\n" % line.strip())
    
    fd.close()
except Exception, e:
    print "Unable to store urls: %s" % (e)
    sys.exit(1)
 
if check_service() != 0:
    print "The script generated an invalid config"
    sys.exit(1)

reload_service()
time.sleep(2)
load_cache()
