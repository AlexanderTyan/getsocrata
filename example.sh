#!/bin/bash

config="sample.config"


source token.sh.auth
python getsocrata.py --token $token --config $config

# unset env variables
unset auth
unset config
