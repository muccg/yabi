set -ex
echo $BASH_SOURCE
echo $-
java -jar /usr/local/closure/compiler.jar --js yabiadmin/yabiadmin/yabifeapp/static/javascript/*.js --js_output_file output.js --summary_detail_level 3
java -jar /usr/local/closure/compiler.jar --js yabiadmin/yabiadmin/yabifeapp/static/javascript/account/*.js --js_output_file output.js --summary_detail_level 3
