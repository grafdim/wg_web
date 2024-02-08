local wgUtils = require("wgParse")
local lummander = require("lummander")
local json = require("lunajson")
local cli = lummander.new({
	title = "Interact with Wireguard Configuration files", -- <string> title for CLI. Default: ""
	theme = "acid",
})

cli:command("json <cfg_file>", "Convert the wireguard configuration <cfg_file> into json.")
	:action(function(parsed, command, app)
		print(json.encode(wgUtils.parse(parsed.cfg_file)))
	end)

cli:command("delete <peer_id> <cfg_file>", "Delete Peer <peer_id>  from <cfg_file> configuration file")
	:action(function(parsed, command, app)
		local conf = wgUtils.parse(parsed.cfg_file)
		wgUtils.deletePeer(conf, parsed.peer_id)
		print(wgUtils.compileConfig(conf))
	end)

cli:command(
	"add <peer_id> <public_key> <preshared_key> <allowed_ip> <cfg_file>",
	"Add a Peer with the relevant parameters to wireguard <cfg_file> config file"
):action(function(parsed, command, app)
	local cfg = wgUtils.parse(parsed.cfg_file)
	local user_params = {
		["PresharedKey"] = parsed.preshared_key,
		["PublicKey"] = parsed.public_key,
		["AllowedIPs"] = parsed.allowed_ip,
	}
	wgUtils.insertPeer(cfg, parsed.peer_id, user_params)
	print(wgUtils.compileConfig(cfg))
end)

cli:parse(arg)
