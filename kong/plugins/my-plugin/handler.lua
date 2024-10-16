local http  = require("resty.http")
local cjson = require("cjson.safe")
local access = require("kong.plugins.my-plugin.access")
local body_filter = require("kong.plugins.my-plugin.body_filter")

local MyPluginHandler = {
    PRIORITY = 100,
    VERSION = "0.0.1"
}

-- https://docs.konghq.com/gateway/latest/plugin-development/custom-logic/

-- function MyPluginHandler:response(conf)

--     kong.log.info("response handler")

--     local http_client = http.new()
--     local res, err = http_client:request_uri("https://httpbin.konghq.com/anything", {
--         method = "GET",
--         headers = {
--             ["Content-Type"] = "application/json"
--         }
--     })
--     if err then
--         kong.log.err("failed to request: ", err)
--         return kong.response.err(500, "Error when trying to access 3rd party service: " .. err, {
--             ["Content-Type"] = "application/json"
--         })
--     end
    
--     local body, err = cjson.decode(res.body)
--     if err then 
--         return kong.response.err(500, "Error when trying to decode response body: " .. err, {
--             ["Content-Type"] = "application/json"
--         })
--     end

--     kong.log.info("name: ", conf.name)
--     kong.response.set_header(conf.response_header_name, body.url)
-- end

function MyPluginHandler:init_worker()
    -- Implement logic for the init_worker phase here (http/stream)
    kong.log("init_worker")
  end
  
  function MyPluginHandler:configure(configs)
    -- Implement logic for the configure phase here
    --(called whenever there is change to any of the plugins)
    kong.log("configure")
  end
  
  function MyPluginHandler:preread(config)
    -- Implement logic for the preread phase here (stream)
    kong.log("preread")
  end
  
  function MyPluginHandler:certificate(config)
    -- Implement logic for the certificate phase here (http/stream)
    kong.log("certificate")
  end
  
  function MyPluginHandler:rewrite(config)
    -- Implement logic for the rewrite phase here (http)
    kong.log("rewrite")
  end
  
--   function MyPluginHandler:access(config)
--     -- Implement logic for the access phase here (http)
--     kong.log("access")
--   end
  
  function MyPluginHandler:ws_handshake(config)
    -- Implement logic for the WebSocket handshake here
    kong.log("ws_handshake")
  end
  
  function MyPluginHandler:header_filter(config)
    -- Implement logic for the header_filter phase here (http)
    kong.log("header_filter")
  end
  
  function MyPluginHandler:ws_client_frame(config)
    -- Implement logic for WebSocket client messages here
    kong.log("ws_client_frame")
  end
  
  function MyPluginHandler:ws_upstream_frame(config)
    -- Implement logic for WebSocket upstream messages here
    kong.log("ws_upstream_frame")
  end
  
  function MyPluginHandler:body_filter(config)
    -- Implement logic for the body_filter phase here (http)
    kong.log("body_filter")
  end
  
  function MyPluginHandler:log(config)
    -- Implement logic for the log phase here (http/stream)
    kong.log("log")
  end
  
  function MyPluginHandler:ws_close(config)
    -- Implement logic for WebSocket post-connection here
    kong.log("ws_close")
  end

-- MyPluginHandler.access = access.access
MyPluginHandler.body_filter = body_filter

return MyPluginHandler

-- https://docs.konghq.com/gateway/3.8.x/plugin-development/custom-logic/#plugins-execution-order

---- Check the plugin is available on server
-- curl -s localhost:8001 | jq '.plugins.available_on_server."my-plugin"'

---- Add a new service
-- curl -is -X POST http://localhost:8001/services --data name=example_service --data url='https://httpbin.konghq.com'

---- Associate the custom plugin(my-plugin) with the example_service service
-- curl -is -X POST http://localhost:8001/services/example_service/plugins --data 'name=my-plugin' --data 'config.response_header_name=X-CustomHeaderName'

---- Add a new route for sending requests through the example_service
-- curl -i -X POST http://localhost:8001/services/example_service/routes --data 'paths[]=/mock' --data name=example_route


------------ Test result
-- curl -i http://localhost:8000/mock/anything
