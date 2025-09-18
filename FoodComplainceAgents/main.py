import sys
import json
import subprocess
import base64

def run_agent(agent_name, args):
    command = ["python3", f"/home/student_01_ab8595ac0887/hackathon_project/{agent_name}"] + args
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Error executing {agent_name}: {stderr.decode('utf-8')}")
    try:
        return json.loads(stdout.decode('utf-8'))
    except json.JSONDecodeError:
        raise Exception(f"Invalid JSON output from {agent_name}: {stdout.decode('utf-8')}")

def main(text_block):
    # Step 1: Extract context from text
    context_data = run_agent("llm_helper.py", ["extract_context", text_block])
    if "error" in context_data:
        print(json.dumps({"error": context_data["error"]}))
        return
    
    food_category = context_data.get("food_category", "Unknown")
    ingredients = context_data.get("ingredients", [])
    
    results = []
    for item in ingredients:
        ingredient = item["name"]
        concentration = item["concentration"]
        final_result = {"ingredient": ingredient}
        try:
            # Step 2: Classify ingredient
            classification_data = run_agent("llm_helper.py", ["classify", ingredient])
            if "error" in classification_data:
                raise Exception(classification_data["error"])
            is_additive = classification_data["is_additive"]
            final_result["is_additive"] = is_additive

            if is_additive:
                # Step 3: Normalize ingredient name
                normalized_data = run_agent("llm_helper.py", ["normalize", ingredient])
                if "error" in normalized_data:
                    raise Exception(normalized_data["error"])
                normalized_ingredient = normalized_data["normalized_ingredient"]
                final_result["normalized_ingredient"] = normalized_ingredient

                # Step 4: Evaluate compliance
                evaluation_result = run_agent("evaluator_agent.py", [normalized_ingredient, concentration, food_category])
                if "error" in evaluation_result:
                    raise Exception(evaluation_result["error"])

                # Step 5: Judge the result
                encoded_eval = base64.b64encode(json.dumps(evaluation_result).encode('utf-8')).decode('utf-8')
                judged_result = run_agent("judge_agent.py", [encoded_eval])
                if "error" in judged_result:
                    raise Exception(judged_result["error"])

                # Step 6: Generate explanation
                encoded_judged = base64.b64encode(json.dumps(judged_result).encode('utf-8')).decode('utf-8')
                explanation = run_agent("llm_helper.py", ["explain", encoded_judged])
                if "error" in explanation:
                    raise Exception(explanation["error"])
                
                final_result.update(judged_result[0])
                final_result.update(explanation)
            else:
                final_result["status"] = "Not an additive"
                final_result["reason"] = "This ingredient is not classified as a food additive."
                final_result["regulation_reference"] = "N/A"

        except Exception as e:
            final_result["error"] = str(e)
            
        results.append(final_result)

    final_output = {
        "food_category": food_category,
        "results": results
    }
    print(json.dumps(final_output, indent=2))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        text_block = sys.argv[1]
        main(text_block)
    else:
        print(json.dumps({"error": "No text block provided"}))
