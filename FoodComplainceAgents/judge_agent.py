import json
import sys
import base64

def judge_evaluation(evaluation_output):
    """
    Reviews the output of the evaluator agent to ensure it meets quality standards.
    """
    try:
        evaluation_data = json.loads(evaluation_output)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON format from evaluator: {e}"}

    if isinstance(evaluation_data, dict) and 'error' in evaluation_data:
        return evaluation_data # Pass through evaluator errors

    if not isinstance(evaluation_data, list):
        return {"error": "Validation failed: Expected a list of results from the evaluator."}

    for result in evaluation_data:
        required_keys = ['ingredient', 'status', 'reason', 'regulation_reference']
        missing_keys = [key for key in required_keys if key not in result]
        if missing_keys:
            return {"error": f"Validation failed: Result is missing required keys: {missing_keys}"}
        
        # Check for clear regulation reference
        if 'N/A' in result['regulation_reference'] or not result['regulation_reference']:
            return {"error": f"Validation failed: Missing regulation reference for {result['ingredient']}. Escalating to human reviewer."}

    return evaluation_data # Return the validated data

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python judge_agent.py <base64_encoded_evaluation_output>"}), file=sys.stderr)
    else:
        try:
            evaluation_output = base64.b64decode(sys.argv[1]).decode('utf-8')
            judged_result = judge_evaluation(evaluation_output)
            print(json.dumps(judged_result, indent=2))
        except Exception as e:
            print(json.dumps({"error": f"Error decoding base64: {e}"}), file=sys.stderr)
