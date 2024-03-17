local lpeg = require("lpeg")
local loc = lpeg.locale()

local wgUtils = {}
local whitespace = (loc.space + "\t") ^ 0

local newline = lpeg.S("\n\r") ^ 1

local binding = lpeg.C(loc.alnum ^ 1)
	* whitespace
	* "="
	* whitespace
	* lpeg.C((loc.alnum + lpeg.S("+=/.:")) ^ 1)
	* whitespace
	/ function(key, val)
		return { [key] = val }
	end

local bindings = binding
	* (binding % function(acc, dict)
		for k, v in pairs(dict) do
			acc[k] = v
		end
		return acc
	end) ^ 0

local interface = "[Interface]" * newline * bindings / function(dict)
	return { ["Interface"] = dict }
end

local peerTag = "[Peer]" * whitespace * "#" * whitespace * lpeg.C(loc.alnum ^ 1)

local peer = peerTag * newline * bindings / function(tag, dict)
	return { [tag] = dict }
end

local peers = peer
	* (peer % function(acc, peerDict)
		for k, v in pairs(peerDict) do
			acc[k] = v
		end
		return acc
	end) ^ 0

local config = interface
	* peers
	/ function(itable, ptable)
		ptable["Interface"] = itable["Interface"]
		return ptable
	end

function wgUtils.parse(filename)
	local f = assert((io.open(filename, "r")), "File does not exist")
	local configuration = f:read("*all")
	f:close()
	return config:match(configuration)
end

function wgUtils.peerIsPresent(wgConfig, peerID)
	return wgConfig[peerID] ~= nil
end

function wgUtils.compileConfig(conf)
	local configTxt = "[Interface]\n"
	for key, val in pairs(conf["Interface"]) do
		configTxt = configTxt .. key .. " = " .. val .. "\n"
	end
	for id, binds in pairs(conf) do
		if id ~= "Interface" then
			configTxt = configTxt .. "[Peer] # " .. id .. "\n"
			for key, val in pairs(binds) do
				configTxt = configTxt .. key .. " = " .. val .. "\n"
			end
		end
	end
	configTxt = configTxt .. "\n"
	return configTxt
end

function wgUtils.deletePeer(conf, peerID)
	assert(conf[peerID] ~= nil, "Peer " .. peerID .. "does not exist!")
	conf[peerID] = nil
end

function wgUtils.insertPeer(conf, peerID, peerParams)
	assert(wgUtils.peerIsPresent(conf, peerID) == false, "Peer ID " .. peerID .. " already in use")
	conf[peerID] = peerParams
end

function wgUtils.getPeer(conf, peerID)
	assert(wgUtils.peerIsPresent(conf, peerID), "Peer does not exist")
	return { [peerID] = conf[peerID] }
end

return wgUtils
