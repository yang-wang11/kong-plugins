local PLUGIN_NAME = "my-plugin"

return {
    name = PLUGIN_NAME,
    fields = {
        {
            config = {
                type = "record",
                fields = {
                    { name = { type = "string", default = "default", required = true } },
                }
            }
        }
    }
}
