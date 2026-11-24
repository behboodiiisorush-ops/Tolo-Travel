#!/bin/bash
# Full chain: render missing frames of every part (house re-rendered for the banner fix), final post, commit.
cd "$(dirname "$0")"
./run_all.sh
cd ..
git add last_bell_real/out
git commit -q -m "Realistic last bell: final film (captions, clean, with sfx)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_0195jcA7K3GmXATgzLTbYzbF"
for i in 1 2 3 4; do git push -q -u origin claude/stick-figure-jo3vsw && break; sleep $((i * 10)); done
echo FINISHED $(date +%T)
