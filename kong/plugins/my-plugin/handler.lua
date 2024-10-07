local MyPluginHandler = {
    PRIORITY = 100,
    VERSION = "0.0.1"
}

function MyPluginHandler:response(conf)
    kong.response.set_header("X-MyPlugin", "response")
    -- kong.log.info("name: ", kong.conf.name)
end

return MyPluginHandler

-- https://docs.konghq.com/gateway/3.8.x/plugin-development/custom-logic/#plugins-execution-order
