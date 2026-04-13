-- 滑动窗口速率限制脚本
-- KEYS[1] = 限流键名
-- ARGV[1] = 限制次数
-- ARGV[2] = 时间窗口(秒)
-- ARGV[3] = 当前时间戳(毫秒)
-- 返回: 1=允许, 0=拒绝

local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

-- 移除过期成员
local window_start = now - window * 1000
redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)

-- 统计当前窗口内请求数
local current = redis.call('ZCARD', key)

if current >= limit then
    return 0
end

-- 加入当前请求，score 和 value 都用时间戳（毫秒精度）
redis.call('ZADD', key, now, now)
-- 设置过期时间，避免僵尸 key
redis.call('EXPIRE', key, window + 1)

return 1
