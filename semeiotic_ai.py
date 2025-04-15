import spacy
import json
import sqlite3

nlp = spacy.load("en_core_web_sm")

# Load schema
with open("schema/eg_schema.json", "r") as f:
    SCHEMA = json.load(f)

def guide_user_abduction(eg):
    """
    Guides the user (Immediate Interpretant, constrained to five senses) to recognize normative relations
    (Dynamic Object, Final Interpretant) and abduct possibilities (Signs). Assesses sensory experience to
    evolve Immediate Interpretant (I.I.) into Dynamic Interpretant (D.I.), prompting hypothesis formation.
    
    Args:
        eg (dict): Existential graph with sheet (Secondness), first_cut (Firstness), double_cut (Thirdness).
    
    Returns:
        str: Guidance message reflecting sensory experience, normative structure, and abductive possibilities.
    """
    # Extract components
    imm_object = eg["sheet"]["value"].split("; ")[0].replace("Immediate: ", "")
    dyn_object = eg["sheet"]["value"].split("; ")[1].replace("Dynamic: ", "")
    sign_value = eg["first_cut"]["value"]
    imm_interpretant = eg["double_cut"]["value"]["immediate"]
    dyn_interpretant = eg["double_cut"]["value"]["dynamic"]
    final_interpretant = eg["double_cut"]["value"]["final"]
    
    # Assess sensory experience (Immediate Interpretant, five senses)
    sensory_cues = infer_sensory_cues(imm_object, dyn_object, sign_value)
    experience = f"Based on what you {sensory_cues}, you seem to feel '{imm_interpretant}'"
    
    # Guide normative relation (Dynamic Object, Final Interpretant)
    norm_context = f"in the context of '{dyn_object}'"
    norm_rule = f"which follows a norm: '{final_interpretant}'"
    
    # Prompt abduction (hypothesize Signs)
    possible_signs = hypothesize_signs(dyn_interpretant, dyn_object)
    abduction = "Could it be that "
    if possible_signs:
        abduction += " or ".join([f"'{sign}'" for sign in possible_signs])
    else:
        abduction += f"'{sign_value}' is the main interpretation"
    abduction += " explains what you’re experiencing?"
    
    # Combine into guidance message
    guidance = f"{experience} {norm_context}, {norm_rule}. {abduction}"
    return guidance

def process_input(text, prior_context=None, mode="modus_ponens"):
    doc = nlp(text)
    sign = [token.text for token in doc]
    
    # Secondness: Sheet (Immediate/Dynamic Objects)
    imm_object = next((token.text for token in doc if token.pos_ == "PRON"), "Unknown")
    if "'m" in sign:
        imm_object = f"{imm_object} be"
    dyn_object = next((token.text for token in doc if token.pos_ in ["VERB", "ADJ"] and token.text != "'m"), "Unknown")
    context = " ".join([t for t in sign if t not in [imm_object, "'m", dyn_object]]) if len(sign) > 2 else ""
    dyn_object = f"{dyn_object} + {context}" if context else dyn_object
    
    # Firstness: First Cut (Sign)
    sign_value = initial_meaning(imm_object, dyn_object, context)
    
    # Thirdness: Double Cut (Interpretants)
    imm_interpretant, dyn_interpretant, final_interpretant = promote_to_interpretants(sign_value, dyn_object, context)
    
    # Build EG per schema
    eg = {
        "sheet": {
            "category": SCHEMA["structure"]["sheet"]["category"],
            "value": f"Immediate: {imm_object}; Dynamic: {dyn_object}"
        },
        "first_cut": {
            "category": SCHEMA["structure"]["first_cut"]["category"],
            "value": sign_value
        },
        "double_cut": {
            "category": SCHEMA["structure"]["double_cut"]["category"],
            "value": {
                "immediate": imm_interpretant,
                "dynamic": dyn_interpretant,
                "final": final_interpretant
            }
        }
    }
    
    # Context shift for normative evolution
    if prior_context and prior_context["sheet"]["value"] != eg["sheet"]["value"]:
        new_dyn_object = differentiate(dyn_object, dyn_interpretant, sign)
        new_sign_value = initial_meaning(imm_object, new_dyn_object, context)
        new_imm_interpretant, new_dyn_interpretant, new_final_interpretant = promote_to_interpretants(new_sign_value, new_dyn_object, context)
        eg["sheet"]["value"] = f"Immediate: {imm_object}; Dynamic: {new_dyn_object}"
        eg["first_cut"]["value"] = new_sign_value
        eg["double_cut"]["value"] = {
            "immediate": new_imm_interpretant,
            "dynamic": new_dyn_interpretant,
            "final": new_final_interpretant
        }
    
    # Abduction: Hypothesize Sign from Interpretant
    if mode == "abduction":
        hypothesized_sign = hypothesize_signs(dyn_interpretant, dyn_object)
        if hypothesized_sign:
            eg["first_cut"]["value"] = hypothesized_sign[0]  # Take first hypothesis
            eg["double_cut"]["value"]["immediate"] = initial_meaning(imm_object, hypothesized_sign[0], context)
    
    # Generate outputs
    output = generate_response(dyn_interpretant)
    guidance = guide_user_abduction(eg)
    
    context = {"sheet": eg["sheet"], "first_cut": eg["first_cut"], "double_cut": eg["double_cut"]}
    
    # Store EG
    save_eg(eg, text)
    
    return output, guidance, context, eg

# Helper functions
def infer_sensory_cues(imm_object, dyn_object, sign_value):
    """Infer likely sensory cues for the Immediate Interpretant."""
    if "pen" in dyn_object and "sign" in dyn_object:
        return "see and feel (the pen being handed)"
    elif "pen" in dyn_object and "gift" in dyn_object:
        return "see and hear (the gift announcement)"
    elif "confused" in dyn_object:
        return "feel (mental fog)"
    elif "nothing" in dyn_object:
        return "sense (lack of focus)"
    elif "done" in dyn_object:
        return "feel (completion)"
    return "sense"

def initial_meaning(imm_obj, dyn_obj, context):
    display_obj = imm_obj.split()[0]
    if "pen" in dyn_obj and "sign" in context:
        return f"{display_obj} is signing"
    elif "pen" in dyn_obj and "gift" in context:
        return f"{display_obj} is gifted"
    elif "confused" in dyn_obj:
        return f"{display_obj} is confused"
    elif "nothing" in dyn_obj:
        return f"{display_obj} is disengaged"
    elif "done" in dyn_obj:
        return f"{display_obj} is finished"
    return f"{display_obj} is processing"

def promote_to_interpretants(sign_value, dyn_object, context):
    imm_interpretant = sign_value
    if "signing" in sign_value:
        dyn_interpretant = "User needs to return pen"
        final_interpretant = "Transaction implies return"
    elif "gifted" in sign_value:
        dyn_interpretant = "User needs to accept gift"
        final_interpretant = "Gift implies obligation"
    elif "confused" in sign_value:
        dyn_interpretant = "User needs help"
        final_interpretant = "Confusion implies resolution"
    elif "disengaged" in sign_value:
        dyn_interpretant = "User needs re-engagement"
        final_interpretant = "Disengagement implies re-engagement"
    elif "finished" in sign_value:
        dyn_interpretant = "User needs closure"
        final_interpretant = "Completion implies closure"
    else:
        dyn_interpretant = f"User needs insight on {dyn_object.split(' + ')[0]}"
        final_interpretant = f"Context implies insight on {dyn_object.split(' + ')[0]}"
    return imm_interpretant, dyn_interpretant, final_interpretant

def generate_response(dyn_interpretant):
    if "return pen" in dyn_interpretant:
        return "Please return the pen after signing."
    elif "accept gift" in dyn_interpretant:
        return "Would you like me to hold the gift pen for you?"
    elif "needs help" in dyn_interpretant:
        return "How can I help?"
    elif "needs re-engagement" in dyn_interpretant:
        return "Keeping it light today, or just taking a breather?"
    elif "needs closure" in dyn_interpretant:
        return "Anything else I can assist with before we wrap up?"
    return "Got it, what’s next?"

def differentiate(dyn_obj, dyn_interpretant, sign):
    base = dyn_obj.split(" + ")[0]
    new_context = " ".join([t for t in sign if t not in ["I", "'m"]]) if len(sign) > 2 else ""
    return f"{base} + {new_context}"

def hypothesize_signs(dyn_interpretant, dyn_object):
    hypotheses = {
        "User needs to return pen": ["I is signing", "I is borrowing"],
        "User needs to accept gift": ["I is gifted", "I is honored"],
        "User needs help": ["I is confused", "I is uncertain"],
        "User needs re-engagement": ["I is disengaged", "I is distracted"],
        "User needs closure": ["I is finished", "I is satisfied"]
    }
    return hypotheses.get(dyn_interpretant, [])

def save_eg(eg, input_text):
    conn = sqlite3.connect("egs.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS egs (input TEXT, eg TEXT)")
    c.execute("INSERT INTO egs VALUES (?, ?)", (input_text, json.dumps(eg)))
    conn.commit()
    conn.close()

def get_eg(input_text):
    conn = sqlite3.connect("egs.db")
    c = conn.cursor()
    c.execute("SELECT eg FROM egs WHERE input = ?", (input_text,))
    result = c.fetchone()
    conn.close()
    return json.loads(result[0]) if result else None

def refine_thirdness():
    conn = sqlite3.connect("egs.db")
    c = conn.cursor()
    c.execute("SELECT eg FROM egs")
    egs = [json.loads(row[0]) for row in c.fetchall()]
    thirdness_values = [eg["double_cut"]["value"]["dynamic"] for eg in egs]
    final_values = [eg["double_cut"]["value"]["final"] for eg in egs]
    if thirdness_values.count("User needs help") > 1:
        return "User expressing uncertainty needs guidance", "Uncertainty implies guidance"
    return thirdness_values[-1] if thirdness_values else None, final_values[-1] if final_values else None
