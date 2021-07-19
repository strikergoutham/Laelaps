# Laelaps
Laelaps is an automated monitoring tool for kong gateway. Laelaps is useful for in house security engineers as it continuously monitor and notify missing/mandatory security plugins around routes/services, new routes and new services. 

### Kong gateway is a popluar microservices API gateway with fast adoption among many companies these days. Few notable features include centralized monitoring , security/ scalable features extended via flexible 'kong plugins'.

### Kong allows multiple ways to configure and adapt, we currently assume current setup is done with db-mode. ( postgres )

 With the help of 'kong plugins', security features such as ratelimiting for end points , implementing CORS, implementing authorization , centralized logging is simplified. Plugins can be attached at various levels. It can be made 'global' which applies to all entities, can be attached at 'service'(per) level, can also be attached at route(end point) level.(most of the time). 
 
 Laelaps Hooks to the postgres database and monitors for notable changes and alerts the internal security team.
 
 ![Laelaps](/images/LaelapsArch.jpg)
 
 
 ## It monitors periodically for the following events :
 
 1. If a route/API endpoint gets deployed/exposed without the mandatory plugin.
 2. If a mandatory plugins is removed from the existing routes/API gateway.
 3. New micro services deployed on the gateway.
 4. New routes defined/deployed onto any service.

In this fast moving agile world, number 3 and 4 helps internal security team to assess the newly added targets for any potential vulnerabiity ASAP. Number 1 and 2 alerts to prevent any authorization/authentiation issues / sensitive data leaks / insecure API configuration.

### All the alerts are notified via slack. 

## Setup :

### Prerequisites :

>> Requires Python 3

>> Runs on both Windows / Linux .

>> install dependencies :
```bash
pip3 install requests python-dotenv
```

### Set the following environment variables  or create a .env file with the same.
```bash
USERNAME_KONG='' #username of the kong schema
PWD_KONG=''   #password to the kong schema
HOST_KONG='' #db host
schema_kong='' #schema name
slack_WebHookURL='' #slack webhook url for receiving the alerts
```
### define which plugins to monitor in the "monitored_plugins.txt" file
example file: 
```bash
CORS
rate-limiting
plugin3
plugin4
```
### we can also whitelist the services / routes to exclude from the mandatory plugin scan. This can be defined inside "whitelist.txt" file.
example whitelist file looks like this.
```bash
{"service1":["route-id1","route-id2"],"service2":[],"service3":["route-id3"]}
```
here, we whitelist two routes "route-id1","route-id2" of service "service1" from mandatory plugin scan. if we want to whitelist the whole service from the scan, we can do as done for service2 with routes as empty list.

#### Now you are ready to run Laelaps! Set it up as cron job for real time monitoring.

#### Snapshot of test results:

![Laelaps](/images/Laelaps4.PNG)

![Laelaps](/images/Laelaps5.PNG)

#### A big thanks to my teammate @akshaya(https://www.linkedin.com/in/akshaya-venkateswara-raja/) who did the initial brainstorming and co owns the code, without her the project would be dead.
