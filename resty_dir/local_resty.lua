-- brew install luarocks 
-- brew install openresty/brew/openresty -- install OpenResty
---- brew services start openresty/brew/openresty
---- brew services list / brew services kill openresty/brew/openresty
---- brew services info openresty/brew/openresty
-- luarocks install lua-resty-openssl

-- brew cleanup openresty

local openssl_digest = require "resty.openssl.digest"
local openssl_pkey = require "resty.openssl.pkey"

local key = ""
local data = ""
local signature = ""

local pkey, _ = openssl_pkey.new(key)
assert(pkey, "Consumer Public Key is Invalid")
local digest = openssl_digest.new("sha256")
assert(digest:update(data))
return pkey:verify(signature, digest)
