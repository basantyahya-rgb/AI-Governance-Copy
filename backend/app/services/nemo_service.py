from nemoguardrails import LLMRails
from nemoguardrails import RailsConfig

config = RailsConfig.from_path("config/guardrails")

rails = LLMRails(config)


def check_prompt(prompt: str):

    response = rails.generate(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response