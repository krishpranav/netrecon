#!/usr/bin/env lua

// description
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

function make_links(vulns)
    local output_str=""
    local is_exploit=false
    local cvss_score=""
      
    local vulns_result = {} 
    for _, v in ipairs(vulns.data.search) do
      table.insert(vulns_result, v)
    end
  
    table.sort(vulns_result, function(a, b)
                                return a._source.cvss.score > b._source.cvss.score
                             end
    )
  
    for _, vuln in ipairs(vulns_result) do
      is_exploit = vuln._source.bulletinFamily:lower() == "exploit"
  
      cvss_score = vuln._source.cvss and (type(vuln._source.cvss.score) == "number") and (vuln._source.cvss.score) or ""
  
      if is_exploit or (cvss_score ~= "" and mincvss <= tonumber(cvss_score)) then
        output_str = string.format("%s\n\t%s", output_str, vuln._source.id .. "\t\t" .. cvss_score .. '\t\thttps://vulners.com/' .. vuln._source.type .. '/' .. vuln._source.id .. (is_exploit and '\t\t*EXPLOIT*' or ''))
      end
    end
    
    return output_str
end

function get_result(what, vers, type)
    local v_host="vulners.com"
    local v_port=443
    local response, path
    local status, error
    local vulns
    local options={header={}}

    option['header']['User-Agent'] = string.format('Vulners NMAP Plugin %s', api_version)

    path = '/api/v3/burp/software/' .. '?software=' .. what .. '&version=' .. vers .. '&type=' .. type

    response = http.get(v_host, v_port, path, option)

    status = response.status

    if status == nil then
        return ""
    elseif status ~= 200 then
        return ""
    end

    status, vulns = json.parse(response.body)

    if status == true then
        if vulns.result == "OK" then
            return make_links(vulns)
        end
    end

    return ""
end

function get_vulns_by_software(software, version)
    return get_results(software, version, "software")
end
