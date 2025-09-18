
import json
import sys
import base64

def format_output(judged_output):
    """
    Formats the judged evaluation into a structured report.

    Args:
        judged_output: The JSON string output from the judge agent.

    Returns:
        A formatted string with the evaluation report.
    """
    try:
        evaluation = json.loads(judged_output)

        if isinstance(evaluation, dict) and 'error' in evaluation:
            return f"Error in evaluation: {evaluation['error']}"

        if not evaluation:
            return "No compliance information found for the given input."

        header = "| Ingredient | Status | Reason | Regulation_Reference |\n|---|---|---|---|"
        rows = []
        for result in evaluation:
            rows.append(f"| {result['ingredient']} | {result['status']} | {result['reason']} | {result['regulation_reference']} |")
        
        return f"{header}\n" + "\n".join(rows)

    except json.JSONDecodeError as e:
        return f"Error decoding judged result: {e}"
    except Exception as e:
        return f"An unexpected error occurred during output formatting: {e}"

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python output_agent.py <base64_encoded_judged_output>")
    else:
        try:
            judged_output = base64.b64decode(sys.argv[1]).decode('utf-8')
            formatted_report = format_output(judged_output)
            print(formatted_report)
        except Exception as e:
            print(f"Error decoding base64: {e}")
