#!/usr/bin/python

import optparse
import subprocess
import re
from datetime import datetime
import pytz
import tzlocal
import dateutil.parser


def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--index", dest="index", help="Index to be monitored.")
    parser.add_option("-l", "--lookup", dest="lookup", help="Lookup index for the last x minutes document timestamp.")
    parser.add_option("-u", "--url", dest="url", help="Elasticsearch server URL")
    (options, args) = parser.parse_args()

    if not options.index:
         parser.error("[-] Please specify the index name --index | -i , use --help for more info.")
    elif not options.lookup:
        parser.error("[-] Lookup threshold in minutes | -l , use --help for more info.")
    elif not options.url:
        parser.error("[-] Please specify the elasticsearch cluster URL --url | -u , use --help for more info.")
    return options

def get_logTimeStamp(logDate):
    d = dateutil.parser.parse(logDate)
    logTimeStamp = d.astimezone(pytz.timezone(str(tzlocal.get_localzone())))
    return str(logTimeStamp)

def get_diff_in_minutes(match):
    d1 = get_logTimeStamp(match).split(".")[0]
    d2 = str(datetime.now()).split(".")[0]

    d1 = datetime.strptime(d1, "%Y-%m-%d %H:%M:%S")
    d2 = datetime.strptime(d2, "%Y-%m-%d %H:%M:%S")

    print("[+] Last updated: " + str(d1))
    print("[+] Current time: " + str(d2))
    result = d2 - d1
    return result.seconds / 60


options = get_arguments()
url = options.url + '/' + options.index + '-*/_search?pretty'
query = url + "-d '@query.json'"

print("URL: " + url)
out = subprocess.check_output(['curl', '-s', '-XGET', url, '-d', '@query.json'])
pattern = "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z"
match = re.findall(pattern, out)

minutes = get_diff_in_minutes(match[0])

if minutes > options.lookup:
    print("[-] Index (" + options.index + ") has exceeded the lookup threshold of " + options.lookup + " mins.")
    exit(1)
else:
    print("[+] Index was updated " + str(minutes) + " minutes ago which is within the lookup threshold of " + options.lookup + " mins.")
    exit(0)

