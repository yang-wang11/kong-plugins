local typedefs = require "kong.db.schema.typedefs"

return {
  name = "myheader",
  fields = {
    { consumer = typedefs.no_consumer },
    { config = {
        type = "record",
        fields = {
          { header_value = { type = "string", default = "roar", }, },
        },
    }, },
  }
}
