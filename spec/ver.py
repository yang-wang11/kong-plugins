import io_exec

def items():
  return [{"name": "a"}, {"name": "b"}, {"name": "kong"}]

# namespace_exists_func = any(ns['name'] == "kong" for ns in items())
namespace_exists_func = lambda: any(ns['name'] == "kong" for ns in items())

namespace_exist_result = io_exec.try_io(
    cmd=namespace_exists_func,
    max_tries=20,
    wait=15
)
print(namespace_exist_result)