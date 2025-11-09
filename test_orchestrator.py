import os
import sys
import time
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--test-id")
parser.add_argument("--regression", action="store_true")
parser.add_argument("--list-tests", action="store_true")
args = parser.parse_args()

# Identifies all tests within the ./tests/.. folder
def discover_test(test_dir="tests"):
    tests = {}
    for file in sorted(os.listdir(test_dir)):
        parsed = file.split('_')
        testid = parsed[2].split('.')[0]
        if parsed[0] == "test" and testid.isdigit():
            tests[testid] = f"{test_dir}/{file}"
    return tests

tests = discover_test()

# Runs a singular test 
def run_test(test_id):
    if not(test_id in tests.keys()): 
        print("Test was not found")
        return
    
    print(f"\nRunning {tests[test_id]} ... \n")
    start = time.time()

    try:
        result = subprocess.run(
            ["python3", f"{tests[test_id]}"],
            capture_output=True,
            text=True,
            check=True
        )
        duration = time.time() - start
        print(f"Test passed  -- {test_id}\nReturn Code: {result.returncode} \nDuration: {round(duration, 2)} seconds")

        return {
            "id": test_id,
            "passed": result.returncode,
            "duration": round(duration, 2),
            "output": result.stdout.strip(),
            "error": result.stderr.strip()
        }
    except subprocess.CalledProcessError as e:
        duration = time.time() - start
        print(f"Test failed -- {test_id}\nReturn Code: 1 \nDuration: {round(duration, 2)} seconds \n {e.stdout}" )
        return {
        "id": test_id,
        "passed": 1,
        "duration": round(duration, 2),
        "output": e.stdout,
        "error": e.stderr
    }

# Runs all tests
def run_all_tests():
    tests = discover_test()
    print(f"Discovered {len(tests)} testfiles. \n")

    results = []
    
    for t in tests.keys():
        result = run_test(t)
        results.append(result)

    passed = [r for r in results if not r["passed"]]
    failed = [r for r in results if r["passed"]]

    print("\n===== TEST SUMMARY =====")
    print(f"Total tests: {len(results)}")
    print(f"Passed: {len(passed)}")
    print(f"Failed: {len(failed)}")
    
    if (len(failed) != 0):
        print("\n===== FAILED TESTS =====")
        for f in failed:
            print("Test ID "+f["id"]+"\n"+f["error"])
        print("FAILURE")
        exit(1)

# Runs a test with a given ID
def run_test_by_id(test_id):
    tests = discover_test()    
    for t in tests.keys():
        if int(test_id) == int(t):
            result = run_test(t)
            if result["passed"]:
                print(result["error"])
            return

    print(f"No test found with test ID {test_id}")

def main():
    if args.regression:
        run_all_tests()
    elif args.test_id:
        run_test_by_id(args.test_id)
    elif args.list_tests:
        print(f"Discovered {len(tests)} testfiles. {tests}")
    else:
        print(f"{sys.argv[1]} is an unspecificed command")

if __name__ == "__main__":
    main()