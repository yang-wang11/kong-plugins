local MyHeader = {
  
}

 MyHeader.PRIORITY = 1000
 MyHeader.VERSION = "1.0.0"
 local cache = kong.cache

 function mycache()
  local ok, err = cache.set("mykey", "myvalue", 3600)

 end

 function MyHeader:header_filter(conf)
   -- do custom logic here
   kong.response.set_header("myheader", conf.header_value)
   kong.log.info("added header: myheader = ", conf.header_value)
 end

 return MyHeader
