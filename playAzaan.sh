#!/usr/bin/env bash
if [ $# -lt 1 ]; then
  echo "USAGE: $0 <azaan-audio-path> [<volume_percent>]"
  exit 1
fi

audio_path="$1"
MAX_PCM=32767
vol=${2:-100}          # percent (0-100). 100 is normal.
if [ "$vol" -lt 0 ]; then vol=0; fi
if [ "$vol" -gt 100 ]; then vol=100; fi
gain=$(( vol * MAX_PCM / 100 ))
root_dir=`dirname $0`

# Run before hooks
for hook in $root_dir/before-hooks.d/*; do
    echo "Running before hook: $hook"
    $hook
done

# Play Azaan audio
mpg123 -q -f "$gain" "$audio_path"

# Run after hooks
for hook in $root_dir/after-hooks.d/*; do
    echo "Running after hook: $hook"
    $hook
done
