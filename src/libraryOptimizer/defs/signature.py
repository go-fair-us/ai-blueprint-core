"""Dynamic DSPy Signature from a library prompt body (seed instructions)."""
from __future__ import annotations

import dspy


def make_generate_signature(
    *,
    name: str,
    instructions: str,
    input_field: str = "scenario",
    input_desc: str = (
        "Concrete repository or digital-object situation to apply the prompt to. "
        "Vary biomedical domain, data type, and repository context."
    ),
    output_field: str = "artifact",
    output_desc: str = (
        "The full response the prompt asks for: free text and/or structured "
        "JSON as specified by the instructions."
    ),
) -> type:
    """Build a Signature class whose docstring is the seed (library) prompt."""
    safe = "".join(c if c.isalnum() or c == "_" else "_" for c in name)[:60]
    return type(
        f"Generate_{safe}",
        (dspy.Signature,),
        {
            "__doc__": instructions,
            "__annotations__": {input_field: str, output_field: str},
            input_field: dspy.InputField(desc=input_desc),
            output_field: dspy.OutputField(desc=output_desc),
        },
    )
