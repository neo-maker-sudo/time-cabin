#!/bin/bash

# "$(dirname "$0")" will be current working directroy
# "$(dirname "dir")" will be current working directory parent directory, which is at project folder
cd "$(dirname "dir")"

supervisord -c /etc/supervisor/conf.d/supervisord.conf