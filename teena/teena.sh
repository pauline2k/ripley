#!/usr/bin/env bash

set -e

echo
echo "------------------------------------------"
echo "  Teena welcomes you  "
echo "------------------------------------------"
echo

echo 'Firefox is the only currently supported browser.  Choose regular browser or headless.'

headless_options=("regular" "headless")

select opt in "${headless_options[@]}"; do
  case ${opt} in
  "headless")
    headless=true
    break
    ;;
  "regular")
    headless=false
    break
    ;;
  *)
    echo "That's not an option, goodbye"
    exit 1
    ;;
  esac
done

echo
echo "Enter a unique snippet of the test file name (e.g., 'roster_photos' or 'e_grades_export')"
echo -n "    > "

read test_suite

echo
echo "Enter your username"
echo
printf "    > "

read -s username

echo
echo "Enter your password"
echo
printf "    > "

read -s password

echo
echo "Teena will now execute tests for ${test_suite}!"

test_suite="*${test_suite}*"
USERNAME="${username}" PASSWORD="${password}" pytest tests/test_${test_suite}.py --browser 'firefox' --headless ${headless}

exit 0
