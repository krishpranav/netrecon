#!/usr/bin/env lua


description = [[
For each available CPE the script prints out known vulns (links to the correspondent info) and correspondent CVSS scores.
Its work is pretty simple:
- work only when some software version is identified for an open port
- take all the known CPEs for that software (from the standard nmap -sV output)
- make a request to a remote server (vulners.com API) to learn whether any known vulns exist for that CPE
 - if no info is found this way - try to get it using the software name alone
- print the obtained info out
NB:
Since the size of the DB with all the vulns is more than 250GB there is no way to use a local db. 
So we do make requests to a remote service. Still all the requests contain just two fields - the 
software name and its version (or CPE), so one can still have the desired privacy.
]]

author = 'krishpranav'
license = 'Same as nmap--see https://nmap.org/book/man-legal.html'
categories = {"vuln", "safe", "external"}

local http = require "http"
local json = require "json"
local string = require "string"
local table = require "table"

local api_version="1.2"
local mincvss=nmap.registry.args.mincvss and tonumber(nmap.registry.args.mincvss) or 0.0

portrule = function(host, port)
    local vers=port.version
    return vers ~= nil and vers.version ~= nil
end