import os
import imp

plugin_path = os.path.dirname(os.path.realpath(__file__))
plugins = list(map(lambda x: x.replace('.py',''), filter(lambda x: x.endswith('.py') and not x == '__init__.py', os.listdir(plugin_path))))

print("Loading the following plugins:", ', '.join(plugins))

for m in plugins:
    M = imp.load_source(m, "%s/%s.py" % (plugin_path, m))


