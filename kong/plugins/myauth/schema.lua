-- schema.lua
local typedefs = require "kong.db.schema.typedefs"

return {
  name = "my-auth-plugin",
  fields = {
    { consumer = typedefs.no_consumer },
    { config = {
        type = "record",
        fields = {
          { username = { type = "string", required = true }, },
          { password = { type = "string", required = true }, },
        },
    }, },
  },
}
