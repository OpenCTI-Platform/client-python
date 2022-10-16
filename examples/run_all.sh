for script in ./*.py; do
  [[ $script == *"cmd_line_tag_latest_indicators_of_threat.py"* ]] && continue;
   python3 $script;
done