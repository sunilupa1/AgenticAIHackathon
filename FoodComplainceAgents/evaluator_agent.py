
import json
import sys
import re
from thefuzz import fuzz

def convert_to_mg_per_kg_or_l(value, unit):
    """Converts a value to mg/kg or mg/L based on its unit."""
    unit = unit.lower().strip()
    if unit in ["mg/kg", "mg/l"]:
        return value
    if unit in ["g/kg", "g/l"]:
        return value * 1000
    if unit in ["kg/kg", "l/l"]:
        return value * 1000000
    return None  # Unit not recognized

def find_best_match(user_input, options):
    """Finds the best match for user input from a list of options using fuzzy matching."""
    user_input = user_input.lower().strip()
    best_match = None
    highest_score = 0
    for option in options:
        score = fuzz.partial_ratio(user_input, option.lower())
        if score > highest_score:
            highest_score = score
            best_match = option
    
    if highest_score >= 70:
        return best_match
    return None

def evaluate_compliance(ingredient, concentration, food_product, regulation_data=None):
    """
    Evaluates the compliance of a food additive based on EU regulations.
    """
    if regulation_data:
        additive_info = {
            "code": ingredient,
            "name": ingredient,
            "food_categories": [
                {
                    "category_name": food_product,
                    "max_level": regulation_data["max_level"]
                }
            ],
            "regulation": regulation_data["source"]
        }
    else:
        json_file_path = "/home/student_01_ab8595ac0887/hackathon_project/food_additives_data_v2.json"
        
        try:
            with open(json_file_path, 'r') as f:
                additives_data = json.load(f)
        except FileNotFoundError:
            return {"error": f"The file {json_file_path} was not found. Please ensure the data file is in place."}
        except json.JSONDecodeError:
            return {"error": f"Failed to decode the JSON from {json_file_path}."}

        # Find the additive in the local data
        additive_info = None
        is_e_number = re.match(r'e\d+', ingredient.lower())
        
        if is_e_number:
            for ad in additives_data:
                if ad.get('code', '').lower() == ingredient.lower():
                    additive_info = ad
                    break
        else:
            highest_score = 0
            for ad in additives_data:
                name_score = fuzz.partial_ratio(ingredient.lower(), ad.get('name', '').lower())
                if name_score > highest_score:
                    highest_score = name_score
                    additive_info = ad
            
            if highest_score < 70:
                additive_info = None

        if not additive_info:
            return {"error": f"Ingredient '{ingredient}' not found in the local food additives database."}

    try:
        concentration_value_str, concentration_unit = concentration.split()
        concentration_value = float(concentration_value_str)
    except ValueError:
        return {"error": f"Invalid concentration format: '{concentration}'. Expected format: '<value> <unit>'"}

    results = []
    # Find matching food category using fuzzy matching
    category_names = [cat.get("category_name", "") for cat in additive_info.get("food_categories", [])]
    best_match_category = find_best_match(food_product, category_names)

    if not best_match_category:
        # Check for globally forbidden additives
        if additive_info.get("max_level") == "Not permitted":
             return [{
                "ingredient": f"{additive_info.get('code', ingredient)} ({additive_info.get('name', ingredient)})",
                "status": "Forbidden",
                "reason": f"{additive_info.get('name', ingredient)} has been removed from the EU positive list and is not permitted in any food category.",
                "regulation_reference": additive_info.get('regulation', 'N/A')
            }]
        return {"error": f"No rules found for ingredient '{ingredient}' in the specified food product '{food_product}'. It may not be authorized for this use."}

    for category in additive_info.get("food_categories", []):
        if category.get("category_name") == best_match_category:
            max_level_str = category.get('max_level', '').strip()
            
            if max_level_str.lower() == 'quantum satis':
                results.append({
                    "ingredient": f"{additive_info.get('code', ingredient)} ({additive_info.get('name', ingredient)})",
                    "status": "Compliant",
                    "reason": f"Authorized under 'quantum satis' (no numerical limit) for food category '{category['category_name']}'. The provided level is acceptable.",
                    "regulation_reference": additive_info.get('regulation', 'N/A')
                })
                continue

            max_level_match = re.search(r'(\d+\.?\d*)\s*(.*)', max_level_str)
            if max_level_match:
                max_level_value = float(max_level_match.group(1))
                max_level_unit = max_level_match.group(2).strip()

                converted_concentration = convert_to_mg_per_kg_or_l(concentration_value, concentration_unit)
                converted_max_level = convert_to_mg_per_kg_or_l(max_level_value, max_level_unit)

                if converted_concentration is None:
                    results.append({"error": f"Unrecognized unit: {concentration_unit}"})
                    continue
                
                if converted_max_level is None:
                    results.append({"error": f"Unrecognized unit in max level: {max_level_unit}"})
                    continue

                if converted_concentration <= converted_max_level:
                    results.append({
                        "ingredient": f"{additive_info.get('code', ingredient)} ({additive_info.get('name', ingredient)})",
                        "status": "Compliant",
                        "reason": f"Requested concentration {concentration} is within the maximum limit of {max_level_str} for food category '{category['category_name']}'.",
                        "regulation_reference": additive_info.get('regulation', 'N/A')
                    })
                else:
                    results.append({
                        "ingredient": f"{additive_info.get('code', ingredient)} ({additive_info.get('name', ingredient)})",
                        "status": "Conditionally allowed",
                        "reason": f"Requested concentration {concentration} exceeds the maximum limit of {max_level_str} for food category '{category['category_name']}'.",
                        "regulation_reference": additive_info.get('regulation', 'N/A')
                    })
            else:
                 results.append({
                    "ingredient": f"{additive_info.get('code', ingredient)} ({additive_info.get('name', ingredient)})",
                    "status": "Conditionally allowed",
                    "reason": f"A non-numerical limit '{max_level_str}' applies for food category '{category['category_name']}'. Manual verification is required.",
                    "regulation_reference": additive_info.get('regulation', 'N/A')
                })

    return results

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Usage: python evaluator_agent.py <ingredient> <concentration> <food_product> [regulation_data]"}), file=sys.stderr)
    else:
        regulation_data = None
        if len(sys.argv) > 4:
            regulation_data = json.loads(sys.argv[4])
        evaluation = evaluate_compliance(sys.argv[1], sys.argv[2], sys.argv[3], regulation_data)
        print(json.dumps(evaluation, indent=2))
