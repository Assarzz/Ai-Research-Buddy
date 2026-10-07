

from .sections import Section, locate_sections

MODEL = "llama3.2:latest"

# The sections we ask the llm to find.
SECTION_NAMES = ["Title", "Authors", "Abstract", "Keywords", "Significance Statement", "Introduction", 
                 "Materials and Methods", "Results", "Discussion", "Conclusions", "Acknowledgement", "References"]

class Paper:
    def __init__(self, raw_text: str, model: str = MODEL):
        self.raw_text = raw_text
        self.sections = locate_sections(raw_text, SECTION_NAMES, MODEL)

        self.title = self.sections["Title"]
        self.abstract = self.sections["Abstract"]



def quick_feedback(paper: Paper) -> dict[Section, list[str]]:
    """Feedback that doesn't require a call to the LLM, which means it can be run after every single time the document has been changed"""
    feedback = {
        paper.title: [],
        paper.abstract: []
    }
    if paper.title.is_found:

        # "Should not exceed from 250 characters"
        if paper.title.character_count() > 250: feedback[paper.title].append("Title should not be longer than 250 characters")

        # "Capitalize initially (all first letters of each word of the title, except prepositions or helping verbs)."
        all_words_capitalized = True
        for word in paper.title.text.split():
            if not word[0].isupper(): all_words_capitalized = False
        if not all_words_capitalized: feedback[paper.title].append("All words In title should be capitalized")
    else:
        feedback[paper.title].append("Title Missing")


    if paper.abstract.is_found:
        # "Should not exceed 300 words"
        if paper.abstract.word_count() > 300: feedback[paper.abstract].append("Abstract should not be longer than 300 words")
        
    else:
        feedback[paper.abstract].append("Abstract Missing")

    return feedback

import json
import ollama



system_instructions = """
You are an expert academic editor. Your task is to critique scientific papers based on strict structural and content guidelines.

Evaluate the provided text against these specific criteria:

### 1. Title & Authors
- Does the title condense the core work concisely? 
- Are author affiliations moving from specific to general (Department -> University -> Country)?
- Is the corresponding author clearly identified?

### 2. Abstract
- Are non-standard abbreviations avoided?
- Are references strictly excluded from the abstract?
- Is it clearly structured into the following sections: Background, Materials and Methods, Results, Conclusions?

### OUTPUT FORMAT
You must respond ONLY with a valid JSON object. Do not include markdown formatting, conversational text, or explanations outside the JSON. Use the exact section names as keys. The values must be a list of strings containing your critiques and actionable advice. 

Example:
{
  "Title": ["The title does not concisely condense the core work.", "The corresponding author is not clearly identified. Add their email."],
  "Abstract": ["References are strictly excluded from the abstract. Remove (Miller et al., 2021).", "The abstract lacks required structure."]
}
"""


def expensive_feedback(paper: Paper, model: str = MODEL) -> dict[Section, list[str]]:
    """Feedback that requires a call to the LLM, it takes like 10-20 seconds so it has to be run in the background and only occasionally"""
    
    feedback = {
        paper.title: [],
        paper.abstract: []
    }
    
    # only send sections to the llm that actually exist
    content_to_review = ""
    if paper.title.is_found:
        content_to_review += f"Title:\n{paper.title.text}\n\n"
    if paper.abstract.is_found:
        content_to_review += f"Abstract:\n{paper.abstract.text}\n\n"
        
    if not content_to_review:
        return feedback # Exit early if the document was completely empty

    # run llm, ollama makes sure we get json response
    try:
        response = ollama.chat(
            # llama3.1:8b
            # qwen3:4b
            model=model,
            messages=[
                {'role': 'system', 'content': system_instructions},
                {'role': 'user', 'content': content_to_review}
            ],
            format='json'
        )
        
        raw_json_string = response['message']['content']
        llm_data = json.loads(raw_json_string)
        
    except Exception as e:
        print(f"Error communicating with Ollama or parsing JSON: {e}")
        return feedback


    section_map = {
        "Title": paper.title,
        "Abstract": paper.abstract
    }
    
    for string_key, critiques in llm_data.items():
        
        if string_key in section_map:
            section_obj = section_map[string_key]
            if isinstance(critiques, list):
                feedback[section_obj].extend(critiques)
            elif isinstance(critiques, str):
                feedback[section_obj].append(critiques)
                
    return feedback


EXAMPLE_PAPER = """
A VERY EXHAUSTIVE AND COMPREHENSIVE STUDY INVESTIGATING THE EFFICACY OF DRUG ND-42 IN LABORATORY MICE MODELS TO PREVENT CELLULAR DEGRADATION IN THE PREFRONTAL CORTEX

Jane Doe, John Smith, Dr. Alan Grant.
Corresponding Author: Jane (jane@email.com)

# The Abstract. 
In this study, we tested ND-42 on laboratory mice to see if it would stop cellular degradation. We gave 50 mice the drug daily for four weeks and compared them to a control group of 50 mice that received a saline placebo. The results showed a 45% decrease in degradation compared to the control group, which aligns with previous findings on similar compounds (Miller et al., 2021). The drug was well-tolerated by the subjects with minimal side effects. We conclude this proves the drug is highly effective for this specific strain of mice and should be considered for further clinical trials.

Keywords: science, biology, mice, laboratory testing, drugs, good results

Significance Statement:
The phosphorylation of the 5-HT2A receptor pathway by the compound ND-42 introduces a highly complex, transcriptomic-altering mechanism for mitigating neuro-degradation in murine models. By upregulating BDNF expression cascades while simultaneously inhibiting the mTOR signaling pathway, we observed a statistically significant alteration of the neuro-chemical landscape of the prefrontal cortex, a finding that fundamentally reshapes our understanding of neuro-pharmacological interventions in advanced stages of cortical atrophy.

Introduction:
### Background of the Study
Cellular degradation in the prefrontal cortex is a major issue in neurobiology. Over the past decade, many drugs have been tested to prevent this degradation, but most have failed due to high toxicity levels in the liver. 

### Statement of the Problem
We wanted to see if ND-42 would work better than the older drugs currently on the market. Currently, there is a lack of effective treatments that do not cause severe hepatic stress. 

### Aims and Objectives
The primary objective of this research is to evaluate the safety profile and efficacy of ND-42. We believe it will work well. The methodology will involve standard testing procedures on a standard murine model. If successful, this could be a new drug on the market.
"""

SHORT_EXAMPLE_PAPER = """
A VERY EXHAUSTIVE AND COMPREHENSIVE STUDY INVESTIGATING THE EFFICACY OF DRUG ND-42 IN LABORATORY MICE MODELS TO PREVENT CELLULAR DEGRADATION IN THE PREFRONTAL CORTEX

Abstract:
In this study, we tested ND-42 on laboratory mice. We gave 50 mice the drug daily for four weeks. The results showed a 45% decrease in degradation compared to the control group (Miller et al., 2021).
"""



# Only runs when this file is started directly (python ai/main.py), not when it is imported.
if __name__ == "__main__":
    paper = Paper(EXAMPLE_PAPER)

    print("Sections found by llm")
    for name, section in paper.sections.items():
        if section.is_found:
            print(f"[{name}] (characters {section.span[0]}-{section.span[1]}):\n{section.text}\n")
        else:
            print(f"[{name}]: not found\n")

    print("Quick feedback")
    quick_f = quick_feedback(paper)
    for section, feedback_list in quick_f.items():
        for f in feedback_list:
            print(f"[{section.name}]: {f}")

    print("Expensive feedback")
    expensive_f = expensive_feedback(paper)
    for section, feedback_list in expensive_f.items():
        for f in feedback_list:
            print(f"[{section.name}]: {f}")
