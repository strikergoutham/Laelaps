import json
import psycopg2
import os
from dotenv import load_dotenv
import requests

load_dotenv()
username_kong = os.getenv('USERNAME_KONG')
pwd_kong = os.getenv('PWD_KONG')
host_kong = os.getenv('HOST_KONG')
schema_kong = os.getenv('SCHEMA_KONG')

slack_WebHookURL = os.getenv('slack_WebHookURL')
slack_headers = {
'Content-Type': 'application/json'
}

with open("monitored_plugins.txt") as f:
    content = f.readlines()
plugins_check = [x.strip() for x in content]

with open("whitelist.txt") as f:
    content = f.read()
service_whitelist = json.loads(content)
plugins_check_op = plugins_check.copy()

final_service_route_map = {}
index = 0

final_result_map = {}
index2 = 0
index3 = 0


def connectKongDB():
    connection_kong_ext = psycopg2.connect(user=username_kong,password=pwd_kong,host=host_kong,port="5432",database=schema_kong)
    getHandleDB = connection_kong_ext.cursor()
    return getHandleDB

def checkGlobalPlugins(db_conn):
    global plugins_check_op
    for plugin in plugins_check:
        query = "SELECT name,id from plugins where name=\'"+plugin+"\' AND service_id is NULL AND route_id is NULL AND consumer_id is NULL AND enabled=true;"
        db_conn.execute(query)
        result=db_conn.fetchall()
        if len(result) > 0:
            plugins_check_op.remove(plugin)

def fetchServiceRouteMap(db_conn):
    global plugins_check_op,final_service_route_map,index
    query = "SELECT id,name from services;"
    db_conn.execute(query)
    result = db_conn.fetchall()
    if len(result) > 0:
        result_dict = dict((y, x) for x, y in result)
        #remove whitelisted services
        if len(service_whitelist) > 0:
            for service in service_whitelist:
                if len(service_whitelist[service]) == 0:
                    if service in result_dict:
                        result_dict.pop(service)
        #get routes of each service
        if len(result_dict) > 0:
            for service in result_dict:
                service_id = result_dict[service]
                query2 = "select r.path_handling,r.id from routes r where service_id = " + "\'" + service_id + "\';"
                db_conn.execute(query2)
                result2 = db_conn.fetchall()
                if len(result2) > 0:
                    result_dict2 = dict((y, x) for x, y in result2)
                    if len(service_whitelist) > 0:
                        if service in service_whitelist:
                            remove = service_whitelist[service]
                            for item in remove:
                                result_dict2.pop(item)
                    final_service_route_map[index] = {}
                    final_service_route_map[index][service] = result_dict2
                    index = index+1

def CheckRoutePlugins(db_conn):
    global plugins_check_op,final_result_map,index3
    for serviceNum in final_service_route_map:
        routes_list = final_service_route_map[serviceNum]
        for service in routes_list:
            temp = {}
            routes_dict = routes_list[service]
            routes = routes_dict.keys()
            if len(routes) == 0:
                continue
            for route_id in routes:
                query = "SELECT name from plugins where route_id=\'"+route_id+"\';"
                db_conn.execute(query)
                result = db_conn.fetchall()
                if len(result) > 0:
                    res_list = [item for t in result for item in t]
                    if all(item in res_list for item in plugins_check_op):
                        continue
                    else:
                        missing_plugs = list(set(plugins_check_op).difference(res_list))
                        temp[route_id] = missing_plugs
            final_result_map[index3] = {}
            final_result_map[index3][service] = temp
            index3 = index3 + 1


def NotifyNewRoute(db_conn):
    if not os.path.exists('timestamp_route.txt'):
        db_conn.execute("select updated_at from routes order by updated_at DESC limit 1 ;")
        record = db_conn.fetchall()
        for each_record in record:
            timestamp = each_record[0]
    else:
        f = open("timestamp_route.txt", "r")
        timestamp = f.read()
        f.close()
    new_route_sql = "select r.paths, s.name from routes r inner join services s on r.service_id= s.id where r.updated_at > '"+str(timestamp)+"';"
    db_conn.execute(new_route_sql)
    newroute_list = db_conn.fetchall()
    for record in newroute_list:
        msg = "\n New route for `SERVICE:` "+ "*" +str(record[1])+"*" +" `API:` "+"*"+str(record[0])+"*"
        SendSLackMessage(msg)
        #print(msg)

    db_conn.execute("select updated_at from routes order by updated_at DESC limit 1 ;")
    record = db_conn.fetchall()
    for each_record in record:
        timestamp_w = each_record[0]
    f = open("timestamp_route.txt", "w")
    f.write(str(timestamp_w))
    f.close()


def NotifyNewService(db_conn):
    if not os.path.exists('timestamp_service.txt'):
        db_conn.execute("select created_at from services order by created_at DESC limit 1 ;")
        record = db_conn.fetchall()
        for each_record in record:
            timestamp = each_record[0]

    else:
        f = open("timestamp_service.txt", "r")
        timestamp = f.read()
        f.close()
    new_service_sql = "select name,created_at from services where created_at > '"+str(timestamp)+"';"
    db_conn.execute(new_service_sql)
    new_service_list = db_conn.fetchall()
    for record in new_service_list:
        msg = "\n `New SERVICE:` "+"*"+str(record[0]) + "*" + " Created at : " + str(record[1])
        SendSLackMessage(msg)
        #print(msg)

    db_conn.execute("select created_at from services order by created_at DESC limit 1 ;")
    record = db_conn.fetchall()
    for each_record in record:
        timestamp_w = each_record[0]
    f = open("timestamp_service.txt", "w")
    f.write(str(timestamp_w))
    f.close()

def SendSLackMessage(msg):
        data = {"text": msg}
        resp = requests.request(method='POST', url=slack_WebHookURL, headers=slack_headers,json=data)

def parsePluginResults():
    for i in range(0,len(final_result_map)):
        temp = final_result_map[i]
        for i, k in enumerate(temp):
            if len(temp[k]) > 0:
                temp2 = temp[k]
                for l,m in enumerate(temp2):
                    #print("Route: ", m)
                    #print("Missing Plugins: ",temp2[m])
                    msg = "\n[+]Service: "+ "*" + k +"*" + " Route ID: "+"*" + m + "*" + " Missing Plugins: " + "*" + str(temp2[m]) +"*"
                    SendSLackMessage(msg)
            else:
                continue

if __name__ == "__main__":
    SendSLackMessage("*[+]Laelaps Kong Gateway Monitoring started. *")
    db_conn = connectKongDB()
    SendSLackMessage("\n*[+]Monitoring routes with missing plugins... *")
    checkGlobalPlugins(db_conn)
    fetchServiceRouteMap(db_conn)
    CheckRoutePlugins(db_conn)
    parsePluginResults()
    SendSLackMessage("\n*[+]Scanning for new Routes... *")
    NotifyNewRoute(db_conn)
    SendSLackMessage("\n*[+]Scanning for new Services... *")
    NotifyNewService(db_conn)