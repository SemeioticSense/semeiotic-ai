# Semeiotic AI: Existential Graph Framework

## Overview

A semeiotic AI model using Peircean existential graphs to process inputs, guide sensory Immediate Interpretants (I.I.), and support abduction for scientific theory development. The I.I. is constrained to five senses, evolving to Dynamic Interpretants via normative rules.

Files:
- [eg_schema.json](./schema/eg_schema.json): Defines EGs and sensory I.I.
- [semeiotic_ai.py](./semeiotic_ai.py): Processes inputs.
- [requirements.txt](./requirements.txt): Lists dependencies.
- [LICENSE](./LICENSE): MIT License.

## Installation

```bash
git clone https://github.com/SemeioticSense/semeiotic-ai.git
cd semeiotic-ai
pip install -r requirements.txt
python -m spacy download en_core_web_sm

from semeiotic_ai import process_input
output, guidance, _, _ = process_input("The teller gives me a pen as a gift")
print(guidance)

