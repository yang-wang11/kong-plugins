local helpers = require "spec.helpers"

describe("my-plugin", function()
    local client

    -- 在每个测试之前启动 Kong
    setup(function()
        local bp = helpers.get_db_utils() -- 获取测试环境
        bp.plugins:insert {
            name = "my-plugin",       -- 插件名称
            config = {
                my_config_param = "value"
            }
        }

        local route1 = bp.routes:insert {
            hosts = { "test1.com" }
        }

        bp.services:insert {
            name = "service1",
            host = "httpbin.org"
        }

        assert(helpers.start_kong())
    end)

    -- 在每个测试结束时停止 Kong
    teardown(function()
        helpers.stop_kong()
    end)

    it("tests my plugin", function()
        -- 发起 HTTP 请求
        client = helpers.proxy_client()

        local res = client:get("/get", {
            headers = { host = "test1.com" }
        })

        assert.res_status(200, res) -- 断言响应状态码为 200
    end)
end)
