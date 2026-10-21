import json
from collections.abc import Iterator

import ollama
import pymupdf

# So basically qwen3-vl and qwen3.5 models both support text as well as images natively. So we just divide the pdf into a couple of images and pass them. 
# qwen3.5 is seemingly better and faster but it refuses to cache the loaded pdf.
# Caching means the pdf only needs to be loaded once for the first chat, and doesn't have to be reloaded for every new message in the chat (which would be the case with qwen3.5 models that fail to cache), saving like 20 seconds for every chat after the first one. (It takes a long time to read a pdf full of images)
# If we had all criteria bunched together from the start, we could just pass them all at once and then caching doesn't matter and qwen3.5 is for sure better.
DEFAULT_MODEL = "qwen3-vl:2b-instruct-q8_0"

SYSTEM_PROMPT = """You are an examiner evaluating an academic paper. The paper is attached as images, one per page, in page order (image 1 is page 1). Base every judgement only on what the paper actually contains. Be strict rather than lenient."""

TASK = """Does the paper fulfill this criterion?
Criterion: {criterion}

First explain your reasoning in one to three plain sentences, then the verdict: "fulfilled", "partially" (addressed but incompletely) or "not_fulfilled" (not addressed or contradicted)."""

# Reasoning fields come before the verdict so the model reasons before it commits.
# maxLength stops small models from looping on the same sentence until num_predict cuts them off.
SCHEMA = {
    "type": "object",
    "properties": {
        "explanation": {"type": "string", "maxLength": 600},
        "verdict": {"type": "string", "enum": ["fulfilled", "partially", "not_fulfilled"]},
    },
    "required": ["explanation", "verdict"],
}


def render_pages(pdf_path: str, max_side: int = 1024) -> list[tuple[bytes, int, int]]:
    """Render every page to PNG with its longest side at most max_side pixels. Returns (png, width, height)."""
    pages = []
    with pymupdf.open(pdf_path) as doc:
        for page in doc:
            zoom = min(max_side / max(page.rect.width, page.rect.height), 200 / 72)  # cap at 200 dpi
            pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
            pages.append((pix.tobytes("png"), pix.width, pix.height))
    return pages


def context_size(pages: list[tuple[bytes, int, int]]) -> int:
    """Context window for the paper plus room for a criterion and answer, rounded up.

    It depends only on the paper, so all criteria use the same value: changing num_ctx
    reloads the model and discards the cached pages. Ollama silently truncates prompts
    that don't fit, so this errs on the large side (one token per 28x28 pixel patch)."""
    tokens = sum(w * h / 784 for _, w, h in pages) + 4096
    return int(tokens // 4096 + 1) * 4096


def evaluate(
    pdf_path: str,
    criteria: list[str],
    model: str = DEFAULT_MODEL,
    max_side: int = 1024,
    host: str | None = None,
) -> Iterator[dict]:
    """Yield one result per criterion as each one finishes, not all at once,  on the form:
    {"criterion", "verdict", "explanation"}.

    verdict is None if the model's answer was cut off (no usable judgement).
    Raises ollama.ResponseError (e.g. model not pulled) or ConnectionError (Ollama not running).
    """

    pages = render_pages(pdf_path, max_side)
    client = ollama.Client(host=host)
    paper = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"The paper ({len(pages)} pages):", "images": [png for png, _, _ in pages]},
    ]
    options = {"num_ctx": context_size(pages), "temperature": 0, "num_predict": 1024}

    for criterion in criteria:
        response = client.chat(
            model=model,
            messages=paper + [{"role": "user", "content": TASK.format(criterion=criterion)}],
            format=SCHEMA,
            think=False,
            keep_alive="15m",
            options=options,
        )
        try:
            result = json.loads(response.message.content)
        except json.JSONDecodeError:  # only if the answer was cut off at num_predict
            result = {"explanation": "The model's answer was cut off.", "verdict": None}
        yield {"criterion": criterion, **result}

from timeit import default_timer as timer

# run `python -m ai.pdf_evaluate` after downloading some example pdf and changing the `pdf_path` to point to it
if __name__ == "__main__":

    # Example pdf that shouldn't be uploaded to github, it can be downloaded at `https://scialert.net/fulltext/fulltextpdf.php?pdf=knowledgia/ajaps/2023/101-106.pdf`
    pdf_path = "Review Article Ab Initio Method for Estimating the Theoretical Hardness of Covalent Crystals with a Cubic Structure.pdf"

    # it straight up just lies but ok.
    criterias = ["All pages have a page number", "The paper is max 5 pages"]
    start = timer()
    for i, r in enumerate(evaluate(pdf_path, criterias), 1):
        print(f"{(timer()-start):.2f} secs")
        start = timer()
        verdict = f"[{r["verdict"]}]" if r["verdict"] else "[ERROR]"
        print(f"{i}. {r['criterion']}\n   {verdict}: {r['explanation']}\n")