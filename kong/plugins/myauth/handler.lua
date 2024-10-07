-- handler.lua
local MyAuthHandler = {
  PRIORITY = 900,  -- 插件的优先级
  VERSION = "1.0.0",
}

function MyAuthHandler:access(conf)
  local req_username = kong.request.get_header("username")
  local req_password = kong.request.get_header("password")

  if conf.username ~= req_username or conf.password ~= req_password then
    kong.log.warn("Unauthorized for user ", tostring(req_username), " with password ", tostring(req_password))
  end
  -- print the username and password to the log
  

  kong.log("Authorized for user ", tostring(req_username), " with password ", tostring(req_password))

end

return MyAuthHandler
