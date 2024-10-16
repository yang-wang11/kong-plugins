local PLUGIN_NAME = "my-plugin"
local typedefs = require "kong.db.schema.typedefs"

return {
    name = PLUGIN_NAME,
    fields = {
        {
            config = {
                type = "record",
                fields = {
                    { name = { type = "string", default = "default", required = true } },
                    { response_header_name = typedefs.header_name { required = false, default = "X-MyPlugin" } },
                }
            }
        }
    }
}
