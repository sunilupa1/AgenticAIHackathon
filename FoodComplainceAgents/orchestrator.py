import subprocess
import json
import sys
import re
from default_api import google_web_search

def search_online_for_regulation(ingredient, food_product):
    """Searches online for EU regulations regarding the ingredient."""
    for attempt in range(3):
        try:
            query = f"EU regulation for {ingredient} in {food_product}"
            search_results = google_web_search(query=query)
            if search_results and search_results.get("google_web_search_response", {}).get("output"):
                # Naive parsing of search results. This should be improved with more sophisticated NLP techniques.
                output = search_results.get("google_web_search_response", {}).get("output")
                max_level_match = re.search(r'(\d+\.?\d*)\s*mg/kg', output)
                if max_level_match:
                    return {"max_level": f"{max_level_match.group(1)} mg/kg"}
        except Exception:
            pass  # Ignore exceptions and retry
    return None

def orchestrate_evaluation(query):
    """
    Orchestrates the evaluation of a food additive compliance query.

    Args:
        query: The user query (e.g., "Can I use E220 in dried apricots at 2500 mg/kg?").

    Returns:
        A formatted string with the evaluation result.
    """
    # Orchestrator Agent: Extract structured input
    try:
        parts = query.split(" at ")
        concentration_part = parts[1].strip().rstrip('?')
        # Handle cases like "50 mg/L"
        concentration_parts = concentration_part.split(" ")
        concentration = f"{concentration_parts[0]} {concentration_parts[1]}"

        parts = parts[0].split(" in ")
        food_product = parts[1].strip()
        ingredient = parts[0].replace("Can I use", "").strip()

    except (ValueError, IndexError) as e:
        return f"Error parsing query: {e}. Please use the format 'Can I use [Ingredient] in [Food Product] at [Concentration] [Unit]?'"

    # First attempt to evaluate with local data
    evaluator_process = subprocess.Popen(
        ['python3', '/home/student_01_ab8595ac0887/hackathon_project/evaluator_agent.py', ingredient, concentration, food_product],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    evaluator_stdout, evaluator_stderr = evaluator_process.communicate()

    if evaluator_process.returncode != 0:
        return f"Error executing evaluator agent: {evaluator_stderr.decode('utf-8')}"

    evaluator_result = json.loads(evaluator_stdout.decode('utf-8'))

    # If ingredient not found, search online
    if isinstance(evaluator_result, dict) and "error" in evaluator_result and "not found in the local" in evaluator_result["error"]:
        online_regulation = search_online_for_regulation(ingredient, food_product)
        if online_regulation:
            evaluator_process = subprocess.Popen(
                ['python3', '/home/student_01_ab8595ac0887/hackathon_project/evaluator_agent.py', ingredient, concentration, food_product, json.dumps(online_regulation)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            evaluator_stdout, evaluator_stderr = evaluator_process.communicate()

            if evaluator_process.returncode != 0:
                return f"Error executing evaluator agent after online search: {evaluator_stderr.decode('utf-8')}"
            
            evaluator_result = json.loads(evaluator_stdout.decode('utf-8'))
        else:
            return f"Ingredient '{ingredient}' not found in the local food additives database or online. Escalating to human reviewer."

    # Judge Agent
    judge_process = subprocess.Popen(
        ['python3', '/home/student_01_ab8595ac0887/hackathon_project/judge_agent.py', json.dumps(evaluator_result)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    judge_stdout, judge_stderr = judge_process.communicate()

    if judge_process.returncode != 0:
        return f"Error executing judge agent: {judge_stderr.decode('utf-8')}"

    judged_result = json.loads(judge_stdout.decode('utf-8'))

    if isinstance(judged_result, dict) and 'error' in judged_result:
        return f"Evaluation failed. Error: {judged_result['error']}. Escalating to human reviewer."

    # Output Agent
    output_process = subprocess.Popen(
        ['python3', '/home/student_01_ab8595ac0887/hackathon_project/output_agent.py', json.dumps(judged_result)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output_stdout, output_stderr = output_process.communicate()

    if output_process.returncode != 0:
        return f"Error executing output agent: {output_stderr.decode('utf-8')}"

    return output_stdout.decode('utf-8')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        user_query = ' '.join(sys.argv[1:])
        result = orchestrate_evaluation(user_query)
        print(result)
    else:
        print("Usage: python orchestrator.py <user_query>")
