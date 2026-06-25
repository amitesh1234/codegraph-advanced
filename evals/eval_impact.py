from dotenv import load_dotenv

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services import impact_of_change
from evals.cases import IMPACT_CASES
from deepeval import evaluate
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval
from deepeval.models import AnthropicModel
load_dotenv()  

judge = AnthropicModel(model="claude-sonnet-4-6", temperature=0)

def build_cases():
    cases = []
    for name, depth, expected in IMPACT_CASES:
        actual = impact_of_change(name, depth=depth)          # your tool's output
        cases.append(LLMTestCase(
            input=f"What breaks if I change the '{name}' function?",
            actual_output=str(actual),
            expected_output=expected,
        ))
    return cases


coverage = GEval(
    name="ImpactCoverage",
    model=judge,
    criteria=(
        "Does the actual output identify the key functions that depend on the "
        "target function, consistent with the expected blast radius? "
        "Reward correct dependents; penalize missing the important ones."
    ),
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.EXPECTED_OUTPUT,
    ],
)

if __name__ == "__main__":
    evaluate(test_cases=build_cases(), metrics=[coverage])