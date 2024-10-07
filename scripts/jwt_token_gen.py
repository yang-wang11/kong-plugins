import jwt
import datetime

# 定义密钥、算法和声明
secret = "e71829c351aa4242c2719cbfbe671c09"  # 对应你在 hcjwt_secrets 中的 secret
algorithm = "HS256"  # 对应你配置的算法
issuer = "http://local-issuer.com"  # 这里的值应该与 hcjwt_secrets 的 key 保持一致

# 创建声明 (claims)
claims = {
    "iss": issuer,
    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),  # 设置过期时间
    "sub": "testuserid"
}

# 生成 JWT token
token = jwt.encode(claims, secret, algorithm=algorithm)

print(f"Generated JWT Token: {token}")
