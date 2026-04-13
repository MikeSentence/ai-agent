-- 会话额度管理脚本
-- KEYS[1] = 会话额度键名
-- ARGV[1] = 操作类型: get / update / consume
-- ARGV[2] = 金额（update/consume 时有效）
-- ARGV[3] = 初始额度（key 不存在时使用）
-- ARGV[4] = 当天零点的 Unix 时间戳（秒），用于计算 TTL
-- 返回:
--   get     -> 当前额度
--   update  -> 更新后额度
--   consume -> 1=成功 0=额度不足

local key = KEYS[1]
local operation = ARGV[1]
local amount = tonumber(ARGV[2] or '0')
local initial_quota = tonumber(ARGV[3])
local midnight_ts = tonumber(ARGV[4])

-- 确保额度 key 存在，不存在则初始化并设置过期时间到当晚 0 点
local function ensure_quota()
    local exists = redis.call('EXISTS', key)
    if exists == 0 then
        local ttl = midnight_ts - redis.call('TIME')[1]
        if ttl <= 0 then
            ttl = 86400
        end
        redis.call('SET', key, initial_quota, 'EX', ttl)
        return initial_quota
    end
    return tonumber(redis.call('GET', key))
end

if operation == 'get' then
    return ensure_quota()

elseif operation == 'update' then
    local current = ensure_quota()
    local new_quota = current + amount
    redis.call('SET', key, new_quota, 'KEEPTTL')
    return new_quota

elseif operation == 'consume' then
    local current = ensure_quota()
    if current < amount then
        return 0
    end
    local new_quota = current - amount
    redis.call('SET', key, new_quota, 'KEEPTTL')
    return 1

else
    return -1
end
