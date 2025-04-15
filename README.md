# Semeiotic AI: Existential Graph Framework

**By [SemeioticSense](https://github.com/SemeioticSense)**

## Overview

This project implements a semeiotic AI model based on Charles S. Peirce’s existential graphs (EGs). It processes user inputs to guide sensory experiences toward abductive reasoning, supporting scientific theory development. The model structures inputs as:
- **Secondness**: Contextual reality (Immediate/Dynamic Objects).
- **Firstness**: Qualitative Signs.
- **Thirdness**: Interpretants (Immediate, Dynamic, Final).

The **Immediate Interpretant (I.I.)** is constrained to the user’s five senses (sight, sound, touch, taste, smell), evolving into the **Dynamic Interpretant (D.I.)** through normative guidance from the Dynamic Object and Final Interpretant. The AI assesses sensory input to propose hypotheses, enabling users to form theories from evidence.

Key components:
- **[eg_schema.json](./schema/eg_schema.json)**: Defines EGs, sensory I.I., and abduction rules.
- **[semeiotic_ai.py](./semeiotic_ai.py)**: Implements input processing and guidance.
- **[LICENSE](./LICENSE)**: Specifies usage rights (MIT License).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/SemeioticSense/semeiotic-ai.git
   cd semeiotic-ai
