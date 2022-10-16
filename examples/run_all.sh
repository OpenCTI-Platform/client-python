for script in ./*.py; do
#  if [[ $script == *"cmd_line_tag_latest_indicators_of_threat.py"* ]]; then
#    # TODO special execution for cmd tool
#    continue
#  fi
  python3 $script;
done