# Laelaps
Laelaps is an automated monitoring tool for kong gateway. Laelaps is useful for in house security engineers as it continuously monitor and notify missing/mandatory security plugins around routes/services, new routes and new services. 

## Kong gateway is a popluar microservices API gateway with fast adoption among many companies these days. Few notable features include centralized monitoring , security/ scalable features extended via flexible 'kong plugins'.

## Kong allows multiple ways to configure and adapt, we currently assume current setup is done with db-mode. ( postgres )

 With the help of 'kong plugins', security features such as ratelimiting for end points , implementing CORS, implementing authorization , centralized logging is simplified. Plugins can be attached at various levels. It can be made 'global' which applies to all entities, can be attached at 'service'(per) level, can also be attached at route(end point) level.(most of the time). 
 
 Laelaps Hooks to the postgres database and monitors for notable changes and alerts the internal security team.
 
 ![Laelaps](/images/LaelapsArch.jpg)
 
 
 ## It monitors periodically for the following events :
 
 1. If a route gets deployed without the mandatory plugin.
 2. If a mandatory plugins is removed from the existing routes.
 3. New micro services deployed on the gateway.
 4. New routes defined/deployed onto any service.

In this fast moving agile world, number 3 and 4 helps internal security team to assess the newly added targets for any potential vulnerabiity ASAP. Number 1 and 2 alerts to prevent any authorization/authentiation issues / sensitive data leaks / insecure API configuration.

## All the alerts are notified via slack. 

