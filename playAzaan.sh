#!/usr/bin/env bash
if [ $# -lt 1 ]; then
  echo "USAGE: $0 [<volume> 1-100] <azaan-audio-path>"
  exit 1
fi

vol="$1"
audio_path="$2"
root_dir=`dirname $0`
JSONRPC="http://localhost:9000/jsonrpc.js"
UUID="aa:bb:cc:dd:ee"

# Run before hooks
for hook in $root_dir/before-hooks.d/*; do
    #echo "Running before hook: $hook"
    $hook
done

# Play Azaan audio
#omxplayer --vol $vol -o local $audio_path
curl -i -X POST -H "Content-Type: application/json" -d '{"id":1,"params":["'$UUID'",["mixer","volume","'$vol'"]],"method":"slim.request"}' $JSONRPC
curl -i -X POST -H "Content-Type: application/json" -d '{"id":1,"method":"slim.request","params":[ "'$UUID'", ["playlist", "play", "'$audio_path'"] ]}' $JSONRPC
#curl -i -X POST -H "Content-Type: application/json" -d '{"id":1,"method":"slim.request","params":[ "'$UUID'", ["'status'","-",1] ]}' $JSONRPC


 Run after hooks
for hook in $root_dir/after-hooks.d/*; do
    echo "Running after hook: $hook"
    $hook
done
