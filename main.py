from __future__ import print_function
import os
import tempfile
import subprocess
import shutil

INDEX_JS_FILE = 'require(\'{module_name}\')\n'
PACKAGE_JSON_FILE = '{\
  "name": "test1",\
  "version": "1.0.0",\
  "description": "",\
  "main": "index.js",\
  "scripts": {\
    "build": "webpack"\
  },\
  "author": "",\
  "license": "ISC"\
}\
'
WEBPACK_CONFIG_JS_FILE = "var path = require('path');\
var nodeExternals = require('webpack-node-externals');\
\
module.exports = {\
    target: 'node',\
    externals: [\
        nodeExternals({\
            modulesFromFile: {\
                include: ['dependencies']\
            }\
        })\
    ],\
    entry: {\
        main: ['./index.js'],\
    },\
    output: {\
        filename: 'bundle.js',\
        path: path.join(__dirname,'./out')\
    },\
    optimization: {\
        minimize: false\
    },\
    mode: 'none',\
    \
};\
"

def build_bundle_js(module_name, version='latest'):
    path = tempfile.mkdtemp()
    DEVNULL = open(os.devnull, 'wb')
    index_js = open(os.path.join(path, 'index.js'), 'w')
    index_js.write(INDEX_JS_FILE.format(module_name=module_name))
    index_js.close()

    package_json = open(os.path.join(path, 'package.json'), 'w')
    package_json.write(PACKAGE_JSON_FILE)
    package_json.close()

    webpack_config_js = open(os.path.join(path, 'webpack.config.js'), 'w')
    webpack_config_js.write(WEBPACK_CONFIG_JS_FILE)
    webpack_config_js.close()

    p = subprocess.Popen(['npm', 'install', 'webpack-node-externals'], cwd=path, stdout=DEVNULL, stderr=subprocess.STDOUT)
    if p.wait() != 0:
        print('[-] Error: npm install failed')
        return

    p = subprocess.Popen(['npm', 'install', '--save-dev', module_name + '@' + version], cwd=path, stdout=DEVNULL, stderr=subprocess.STDOUT)
    if p.wait() != 0:
        print('[-] Error: npm install failed')
        return

    p = subprocess.Popen(['npm', 'run', 'build'], cwd=path, stdout=DEVNULL, stderr=subprocess.STDOUT)
    if p.wait() != 0:
        print('[-] Error: npm build failed')
        return
    
    f1 = open(os.path.join(path, 'out', 'bundle.js'), 'r')
    buf = f1.read()
    f1.close()

    shutil.rmtree(path, ignore_errors=True)
    DEVNULL.close()
    return buf

if __name__ == "__main__":
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='npm module bundler wrapper')
    parser.add_argument('module_name', type=str,
                    help='moodule name to bundle into one src file')
    parser.add_argument('--module_version', '-v', type=str, nargs='?',
                    help='moodule version to bundle', default='latest')
    parser.add_argument('--output', '-o', type=argparse.FileType('w'), nargs='?',
                    help='output file to write. stdout if not specified', default=sys.stdout)
    
    args = parser.parse_args()
    # print(args)
    buf = build_bundle_js(args.module_name, args.module_version)
    if buf is None:
        sys.exit(1)
    args.output.write(buf + '\n')
    sys.exit(0)