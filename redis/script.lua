local current = redis.call("GET", KEYS[1])
if not current then
    current = 0
end
current = current + tonumber(ARGV[1])
redis.call("SET", KEYS[1], current)
return current

