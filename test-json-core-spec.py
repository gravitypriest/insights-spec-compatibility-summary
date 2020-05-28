import json
import re
from insights.specs import default

with open('/tmp/insights-core-assets/uploader.v2.json') as j:
    json_specs = json.load(j)

core_specs = default.DefaultSpecs()

print('COMMANDS\n==================')

for c in json_specs['commands']:
    if c['symbolic_name'] in dir(core_specs) and 'python -m insights' not in c['command']:
        spec = getattr(core_specs, c['symbolic_name'])

        try:
            spec_cmd = [spec.cmd]
        except AttributeError:
            # print(c['symbolic_name'])
            try:
                spec_cmd = [dep.cmd for dep in spec.deps]
            except AttributeError:
                # installed_rpms
                spec_cmd = [spec.deps[0].cmd]

        json_cmd_regex = re.compile(c['command'])

        match = False
        for thecmd in spec_cmd:
            if json_cmd_regex.match(thecmd):
                match = True
                break
        if match:
            continue
        print c['symbolic_name']
        print('\t' + c['command'])
        print('\t' + ','.join(spec_cmd))
        print('\tREGEX DENIED')


print('==================\nFILES\n==================')


for c in json_specs['files']:
    if c['symbolic_name'] in dir(core_specs):
        spec = getattr(core_specs, c['symbolic_name'])

        try:
            spec_path = [spec.path]
        except AttributeError:
            try:
                spec_path = spec.patterns
            except AttributeError:
                try:
                    spec_path = spec.paths
                except AttributeError:
                    try:
                        spec_path = spec.deps[0].patterns
                    except AttributeError:
                        spec_path = [spec.deps[0].path]

        json_file_regex = re.compile(c['file'])

        # see if regex does it
        match = False
        for p in spec_path:
            thepath = p
            if not p.startswith('/'):
                thepath = '/' + p
            if json_file_regex.match(thepath):
                match = True
                break
        if match:
            continue
        print c['symbolic_name']
        print('\t' + c['file'])
        print('\t' + ','.join(spec_path))
        print('\tREGEX DENIED')

print('==================\nGLOBS\n==================')

for c in json_specs['globs']:
    if c['symbolic_name'] in dir(core_specs):
        spec = getattr(core_specs, c['symbolic_name'])

        try:
            spec_path = [spec.path]
        except AttributeError:
            try:
                spec_path = spec.patterns
            except AttributeError:
                try:
                    spec_path = spec.paths
                except AttributeError:
                    try:
                        spec_path = spec.deps[0].patterns
                    except AttributeError:
                        spec_path = [spec.deps[0].path]

        json_glob_regex = re.compile(c['glob'])

        # see if regex does it
        match = False
        for p in spec_path:
            thepath = p
            if not p.startswith('/'):
                thepath = '/' + p
            if json_glob_regex.match(thepath):
                match = True
                break
        if match:
            continue
        print c['symbolic_name']
        print('\t' + c['glob'])
        print('\t' + ','.join(spec_path))
        print('\tREGEX DENIED')

'''
possible implementation

for commands
1. take values from classic remove.conf
2. do a reverse lookup on a stored uploader.json
3. match the symbolic name to the component
4. disable component

for files...
1. take values from classic remove.conf
2. try to do a reverse lookup and disable component
3. if reverse lookup fails, just load string and let regex handle it
'''