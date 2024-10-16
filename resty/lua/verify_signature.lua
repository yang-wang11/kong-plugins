local openssl_digest = require "resty.openssl.digest"
local openssl_pkey = require "resty.openssl.pkey"


local publicKey = [[
-----BEGIN PUBLIC KEY-----
-----END PUBLIC KEY-----
]]

local jwt_token = ''
local signature = ''

local function RS256T(data, signature, key)
    local pkey, _ = openssl_pkey.new(key)
    assert(pkey, "Consumer Public Key is Invalid")
    local digest = openssl_digest.new("sha256")
    assert(digest:update(data))
    return pkey:verify(signature, digest)
end

print(RS256T(jwt_token, signature, publicKey))