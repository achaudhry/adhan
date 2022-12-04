#!/usr/bin/env bash
if [ $# -lt 1 ]; then
  echo "USAGE: $0 <azaan-audio-path> [<volume>]"
  exit 1
fi

audio_path="$1"
vol=${2:-0}
root_dir=`dirname $0`

# Run before hooks
for hook in $root_dir/before-hooks.d/*; do
    echo "Running before hook: $hook"
    $hook
done

# Play Azaan audio
mpg321 -g $vol $audio_path

# Run after hooks
for hook in $root_dir/after-hooks.d/*; do
    echo "Running after hook: $hook"
    $hook
done
