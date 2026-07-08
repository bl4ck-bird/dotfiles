#!/usr/bin/env bash
# Bisection script: find which test creates an unwanted file or state.
#
# Usage:   ./find-polluter.sh <path_or_pattern_to_check> <test_pattern>
# Example: ./find-polluter.sh '.git' 'src/**/*.test.ts'
#          ./find-polluter.sh 'tmp/leak.json' 'tests/integration/*.test.ts'
#
# The script runs each matching test file individually. Before each run it checks
# whether the target path already exists; if it does, the polluter has been found.
# When the target appears after a test, that test is the polluter.
#
# Prerequisites:
#   - The project uses `npm test <file>` to run a single test file. Override the
#     TEST_CMD env var for other runners that accept a test file path argument.
#       TEST_CMD="pytest" ./find-polluter.sh '/tmp/leak' 'tests/**/test_*.py'
#     go test / cargo test address packages / test targets, not file paths —
#     bisect those manually.
#
# Exit codes:
#   0 = no polluter found
#   1 = polluter identified (or pre-existing pollution — see message)
#   2 = usage error
#
# Apply verification-before-completion: read the script output in your response,
# do not assume "ran fine".

set -e

if [ $# -ne 2 ]; then
  echo "Usage: $0 <path_to_check> <test_pattern>" >&2
  echo "Example: $0 '.git' 'src/**/*.test.ts'" >&2
  exit 2
fi

POLLUTION_CHECK="$1"
TEST_PATTERN="$2"
TEST_CMD="${TEST_CMD:-npm test}"

echo "🔍 Searching for test that creates: $POLLUTION_CHECK"
echo "    Test pattern: $TEST_PATTERN"
echo "    Test command: $TEST_CMD <file>"
echo

# Refuse to run if pollution pre-exists so the bisect starts from a known-clean state.
if [ -e "$POLLUTION_CHECK" ]; then
  echo "❌ Pollution already exists before any test runs:"
  ls -la "$POLLUTION_CHECK"
  echo
  echo "Resolve the pre-existing state first (delete, .gitignore, or fix the cause)."
  echo "Then re-run this script."
  exit 1
fi

# Collect test files. Use find for glob expansion that works across shells.
TEST_FILES=$(find . -path "./$TEST_PATTERN" -type f 2>/dev/null | sort)
if [ -z "$TEST_FILES" ]; then
  # Retry without leading ./ in case the pattern already includes it.
  TEST_FILES=$(find . -path "$TEST_PATTERN" -type f 2>/dev/null | sort)
fi
if [ -z "$TEST_FILES" ]; then
  echo "No test files matched pattern: $TEST_PATTERN" >&2
  exit 2
fi

TOTAL=$(echo "$TEST_FILES" | wc -l | tr -d ' ')
echo "Found $TOTAL test files"
echo

# The while loop runs in a pipeline subshell; every conclusive outcome (polluter
# found, pre-existing pollution) prints and exits inside the loop with status 1,
# and `|| exit 1` propagates that status out of the subshell.
COUNT=0
printf '%s\n' "$TEST_FILES" | while IFS= read -r TEST_FILE; do
  COUNT=$((COUNT + 1))

  if [ -e "$POLLUTION_CHECK" ]; then
    echo "⚠️  Pollution exists before test $COUNT/$TOTAL ($TEST_FILE)"
    echo "    Stopping bisection — investigate the previous test."
    exit 1
  fi

  printf "[%d/%d] %s ... " "$COUNT" "$TOTAL" "$TEST_FILE"

  # Run the test silently; ignore exit code (a failing test is not pollution).
  $TEST_CMD "$TEST_FILE" >/dev/null 2>&1 || true

  if [ -e "$POLLUTION_CHECK" ]; then
    echo
    echo
    echo "🎯 FOUND POLLUTER"
    echo "    Test:    $TEST_FILE"
    echo "    Created: $POLLUTION_CHECK"
    echo
    echo "Pollution details:"
    ls -la "$POLLUTION_CHECK"
    echo
    echo "To investigate further:"
    echo "  $TEST_CMD $TEST_FILE        # Re-run this test in isolation"
    echo "  cat $TEST_FILE              # Review the test code"
    echo "  See: bug-diagnosis/root-cause-tracing.md for the trace process"
    exit 1
  fi

  echo "clean"
done || exit 1

echo
echo "✅ No polluter found among $TOTAL tests."
echo "   The pollution may come from setup/teardown shared state, a global hook,"
echo "   or running tests in combination. Consider running the full suite while"
echo "   watching for the pollution event."
exit 0
