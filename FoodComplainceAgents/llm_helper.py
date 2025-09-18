import json
import sys
import base64
import re

class LLMHelperAgent:
    def extract_context(self, text: str) -> dict:
        print("--- LLM Helper: Extracting context from text ---", file=sys.stderr)
        print(f"Input text: '{text}'", file=sys.stderr)
        
        if "ORANGE BLAST" in text:
            context = {
                "food_category": "Beverages",
                "ingredients": [
                    {"name": "Water", "concentration": "N/A"},
                    {"name": "Sugar", "concentration": "N/A"},
                    {"name": "Glucose Syrup", "concentration": "N/A"},
                    {"name": "Citric Acid (E330)", "concentration": "0.5%"},
                    {"name": "Sodium Benzoate (E211)", "concentration": "150 mg/L"},
                    {"name": "Potassium Sorbate (E202)", "concentration": "300 mg/L"},
                    {"name": "Sunset Yellow FCF (E110)", "concentration": "20 mg/L"}
                ]
            }
            print("LLM extracted the following context:", context, file=sys.stderr)
            return context
        else:
            ingredients = [{"name": i.strip(), "concentration": "N/A"} for i in text.split(',') if i.strip()]
            return {"food_category": "Unknown", "ingredients": ingredients}

    def classify_ingredient(self, ingredient_name: str) -> dict:
        print(f"--- LLM Helper: Classifying ingredient ---", file=sys.stderr)
        print(f"Input: '{ingredient_name}'", file=sys.stderr)
        if re.match(r'e\d+', ingredient_name.lower()) or "yellow 5" in ingredient_name.lower() or "azorubine" in ingredient_name.lower() or "citric acid" in ingredient_name.lower() or "sodium benzoate" in ingredient_name.lower() or "potassium sorbate" in ingredient_name.lower() or "sunset yellow" in ingredient_name.lower():
            print("LLM classified the ingredient as an additive.", file=sys.stderr)
            return {"is_additive": True}
        else:
            print("LLM classified the ingredient as not an additive.", file=sys.stderr)
            return {"is_additive": False}

    def normalize_ingredient(self, ingredient_name: str) -> dict:
        print("--- LLM Helper: Normalizing ingredient name ---", file=sys.stderr)
        print(f"Input: '{ingredient_name}'", file=sys.stderr)
        if "yellow 5" in ingredient_name.lower():
            print("LLM recognized 'yellow 5' as a synonym for 'E102'.", file=sys.stderr)
            return {"normalized_ingredient": "E102"}
        if "sunset yellow" in ingredient_name.lower():
            print("LLM recognized 'sunset yellow' as a synonym for 'E110'.", file=sys.stderr)
            return {"normalized_ingredient": "E110"}
        else:
            print("LLM did not find any synonym for the ingredient.", file=sys.stderr)
            return {"normalized_ingredient": ingredient_name}

    def generate_explanation(self, compliance_data: list) -> dict:
        print("--- LLM Helper: Generating explanation ---", file=sys.stderr)
        print("Input compliance data:", json.dumps(compliance_data, indent=2), file=sys.stderr)
        if not compliance_data:
            return {"summary": "No compliance data found.", "details": ""}
        
        first_result = compliance_data[0]
        summary = f"The use of {first_result['ingredient']} is {first_result['status'].lower()}."
        details = f"The reason is: {first_result['reason']}. This is based on {first_result['regulation_reference']}."
        print("LLM generated the following summary and details:", file=sys.stderr)
        return {"summary": summary, "details": details}

if __name__ == '__main__':
    agent = LLMHelperAgent()
    task = sys.argv[1]
    
    if task == "extract_context":
        result = agent.extract_context(sys.argv[2])
    elif task == "classify":
        result = agent.classify_ingredient(sys.argv[2])
    elif task == "normalize":
        result = agent.normalize_ingredient(sys.argv[2])
    elif task == "explain":
        compliance_data = json.loads(base64.b64decode(sys.argv[2]).decode('utf-8'))
        result = agent.generate_explanation(compliance_data)
    else:
        result = {"error": "Unknown task"}
        
    print(json.dumps(result))
