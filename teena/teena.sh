#!/usr/bin/env bash

set -e

echo
echo "------------------------------------------"
echo "  Teena welcomes you  "
echo "------------------------------------------"
echo

echo 'What kind of browser do we want to use? Enter 1 or 2. '

browser_options=("chrome" "firefox")

select opt in "${browser_options[@]}"; do
  case ${opt} in
  "chrome")
    browser="chrome"
    break
    ;;
  "firefox")
    browser="firefox"
    break
    ;;
  *)
    echo "What did you say?"
    exit 1
    ;;
  esac
done

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
USERNAME="${username}" PASSWORD="${password}" pytest tests/test_${test_suite}.py --browser ${browser} --headless ${headless}

exit 0
