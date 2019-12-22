#!/usr/bin/env python2.7

from flask import Flask,request,jsonify,json
import requests

#########################################################
# MAIN APP
#########################################################

app = Flask(__name__)

#########################################################
# ! ADAPT TO YOUR SETUP !
#########################################################

odl_ip = "10.1.20.144"
odl_port = "8181"
odl_username = "admin"
odl_password = "admin"

#########################################################
# GET THE ROUTE BEST NEXT HOP FROM THE ODL POINT OF VIEW
#########################################################

@app.route('/bgp/route/status', methods=["POST"])
def get_bgp_route():
 #The IP from the user's request is contained in the "text" field
 bgp_route_prefix_slack = request.form["text"]
 
 #We split the CIDR into the prefix part and the subnet part (at the / level) to easily reuse it in our ODL request
 bgp_route_prefix_raw =  bgp_route_prefix_slack.split("/")

 #We end up with the prefix in the first part
 bgp_route_prefix = bgp_route_prefix_raw[0]

 #And the subnet in the secondary part
 bgp_route_subnet = bgp_route_prefix_raw[1]

 #To make sure it's working we can print the below for debug purpose
 #print bgp_route_prefix
 #print bgp_route_subnet

 #Finally we return to Slack the result, the result is called from another function - bgp_route_status - that's
 #where we do the real call to ODL to get the details of the route
 #To do so we pass the prefix and the subnet contained in bgp_route_prefix and bgp_route_subnet
 return bgp_route_status(bgp_route_prefix,bgp_route_subnet)


###############################################################
# THE ODL QUERY BASED ON THE REQUEST RECEIVED FROM SLACK USER
###############################################################

def bgp_route_status(prefix,subnet):

 #This is the ODL URL to query with the prefix from the Slack user's request
 odl_route_status_url = "http://{}:{}@{}:{}/restconf/operational/bgp-rib:bgp-rib/rib/voxbone/loc-rib/tables/bgp-types:ipv4-address-family/bgp-types:unicast-subsequent-address-family/bgp-inet:ipv4-routes/ipv4-route/{}%2F{}/0".format(odl_username,odl_password,odl_ip,odl_port,prefix,subnet)

 #That's when we send the request to ODL with the python module requests
 odl_route_status_request = requests.get(odl_route_status_url)

 #We get the reply from ODL and turn it into JSON
 odl_route_status_request_json = json.loads(odl_route_status_request.text)

 #We extract the next hop value from ODL since this is what we want to have
 next_hop = str(odl_route_status_request_json["bgp-inet:ipv4-route"][0]["attributes"]["ipv4-next-hop"]["global"])

 #Finally we return that value in a nice format
 return str("next_hop : {} ").format(next_hop)


#The app runs on port 5001
if __name__ == "__main__":
   app.run(host='0.0.0.0',port='5001',debug=True)

