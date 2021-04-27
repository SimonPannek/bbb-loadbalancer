# BBB-Loadbalancer
This BBB loadbalancer distributes incoming requests onto different BBB rooms in a list.

It uses multiple Selenium instances to query the current users in all the rooms and picks the one with the least users
currently in it.

_If you are able to access the BBB api, you should probably never use this._
