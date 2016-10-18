#!/bin/bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
bower_dir=$script_dir/bower_components
static_dir=$script_dir/manager/static
css_dir=$static_dir/css
js_dir=$static_dir/js

# install python dependencies
pip install --upgrade -r requirements.txt

# download js/css dependencies
bower install

# make install directory
install -d $css_dir
install -d $js_dir

# install booststrap
install -m644 $bower_dir/bootstrap/dist/css/bootstrap.min.css $css_dir
install -m644 $bower_dir/bootstrap/dist/css/bootstrap.min.css.map $css_dir
install -m644 $bower_dir/bootstrap/dist/js/bootstrap.min.js $js_dir

# install jquery
install -m644 $bower_dir/jquery/dist/jquery.min.js $js_dir

# install tether
install -m644 $bower_dir/tether/dist/js/tether.min.js $js_dir
