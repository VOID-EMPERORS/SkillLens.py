import re
from typing import Optional
import fitz


SKILL_ALIASES = {
    "Python": ["python", "python3", "python 3"],
    "C": ["c language", "language c", "programming in c"],
    "C++": ["c++", "cpp"],
    "Java": ["java programming", "java"],
    "JavaScript": ["javascript", "java script", "js"],
    "TypeScript": ["typescript", "type script"],
    "SQL": ["structured query language", "sql"],
    "HTML": ["html5", "html"],
    "CSS": ["css3", "css"],
    "React": ["react.js", "reactjs", "react"],
    "Node.js": ["node.js", "nodejs", "node js"],
    "Flask": ["flask"],
    "Django": ["django"],
    "FastAPI": ["fastapi", "fast api"],
    "REST APIs": ["restful apis", "restful api", "rest apis", "rest api"],
    "Git": ["git version control", "git"],
    "GitHub": ["github"],
    "Linux": ["linux"],
    "Docker": ["docker", "containerization"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["amazon web services", "aws"],
    "Azure": ["microsoft azure", "azure cloud", "azure"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning"],
    "Natural Language Processing": ["natural language processing", "nlp"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Matplotlib": ["matplotlib"],
    "Scikit-learn": ["scikit-learn", "scikit learn", "sklearn"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "OpenCV": ["opencv", "open cv"],
    "MongoDB": ["mongodb", "mongo db"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MySQL": ["mysql"],
    "SQLite": ["sqlite"],
    "Data Structures": ["data structures", "data structure", "dsa"],
    "Algorithms": ["algorithm design", "algorithms", "algorithm"],
    "Object-Oriented Programming": ["object-oriented programming", "object oriented programming", "oop"],
    "Problem Solving": ["problem-solving", "problem solving"],
    "Communication": ["communication skills", "communication"],
    "Excel": ["microsoft excel", "excel"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Figma": ["figma"],
    "UI/UX Design": ["user experience design", "user interface design", "ui/ux", "ui ux"],
    "Cybersecurity": ["cybersecurity", "cyber security", "information security"],
    "Networking": ["computer networking", "networking"],
    "Testing": ["software testing", "unit testing", "testing"],
    "Agile": ["agile methodology", "scrum", "agile"],
    "Communication Skills": ["written communication", "verbal communication"],
    "Critical Thinking": ["critical thinking"],
    "Project Management": ["project management"],
    "Data Visualization": ["data visualization", "data visualisation"],
    "Statistics": ["statistics", "statistical analysis"],
    "Excel VBA": ["excel vba", "vba"],
}

_ALIAS_LOOKUP = sorted(
    [(canonical, alias.lower().strip()) for canonical, aliases in SKILL_ALIASES.items() for alias in aliases],
    key=lambda x: len(x[1]), reverse=True
)


def extract_resume_text(file_bytes: bytes, filename: str) -> str:
    """Extract text from PDF or TXT uploaded file bytes."""
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext == "txt":
        return file_bytes.decode("utf-8", errors="replace")
    if ext == "pdf":
        try:
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                return "\n".join(page.get_text("text") for page in doc)
        except Exception as exc:
            raise ValueError("The PDF could not be read. Check that it is a valid, non-password-protected PDF.") from exc
    raise ValueError("Unsupported file format. Upload a PDF or TXT file.")


def _has_alias(text: str, alias: str) -> bool:
    escaped = re.escape(alias).replace(r"\ ", r"\s+")
    return re.search(rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])", text, flags=re.IGNORECASE) is not None


def extract_skills(text: str) -> list[str]:
    found = set()
    for canonical, alias in _ALIAS_LOOKUP:
        if canonical not in found and _has_alias(text, alias):
            found.add(canonical)
    return [name for name in SKILL_ALIASES if name in found]


def _load_sentence_model():
    """Load a compact local sentence-transformers model; return None if unavailable."""
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    except Exception:
        return None


def _semantic_scores(resume_text: str, required_skills: list[str]) -> dict[str, float]:
    """Compare each required skill phrase with the resume using sentence embeddings."""
    model = _load_sentence_model()
    if model is None:
        return {}
    try:
        # Compare each skill's meaning to resume chunks; maximum similarity avoids long-document dilution.
        chunks = _chunk_text(resume_text)
        if not chunks:
            return {}
        chunk_embeddings = model.encode(chunks, normalize_embeddings=True, show_progress_bar=False)
        skill_embeddings = model.encode(
            [f"Experience or knowledge with {skill}" for skill in required_skills],
            normalize_embeddings=True, show_progress_bar=False
        )
        scores = {}
        for i, skill in enumerate(required_skills):
            sims = chunk_embeddings @ skill_embeddings[i]
            scores[skill] = float(max(sims))
        return scores
    except Exception:
        return {}


def _chunk_text(text: str, max_words: int = 90) -> list[str]:
    # Split by paragraphs/sentences, then group to keep embedding inputs short and contextual.
    pieces = [p.strip() for p in re.split(r"[\n\r]+|(?<=[.!?])\s+", text) if p.strip()]
    chunks, current, count = [], [], 0
    for piece in pieces:
        words = piece.split()
        if len(words) > max_words:
            for start in range(0, len(words), max_words):
                chunks.append(" ".join(words[start:start + max_words]))
            continue
        if current and count + len(words) > max_words:
            chunks.append(" ".join(current))
            current, count = [], 0
        current.append(piece)
        count += len(words)
    if current:
        chunks.append(" ".join(current))
    return chunks


def analyze_resume_job(
    resume_text: str,
    job_description: str,
    use_semantic: bool = True,
    threshold: float = 0.58,
) -> dict:
    """Analyze explicit skill matches and optionally augment them with semantic similarity."""
    resume_skills = extract_skills(resume_text)
    required_skills = extract_skills(job_description)
    resume_skill_set = set(resume_skills)
    semantic_scores = _semantic_scores(resume_text, required_skills) if use_semantic and required_skills else {}

    matched, missing, details = [], [], {}
    for skill in required_skills:
        if skill in resume_skill_set:
            matched.append(skill)
            details[skill] = {"method": "Explicit keyword", "similarity": 1.0}
        else:
            score: Optional[float] = semantic_scores.get(skill)
            if score is not None and score >= threshold:
                matched.append(skill)
                details[skill] = {"method": "Semantic similarity", "similarity": score}
            else:
                missing.append(skill)
                details[skill] = {
                    "method": "Not matched" if score is None else "Below threshold",
                    "similarity": score,
                }

    score = (len(matched) / len(required_skills) * 100) if required_skills else 0.0
    return {
        "resume_skills": resume_skills,
        "required_skills": required_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "match_percentage": round(score, 1),
        "skill_details": details,
        "semantic_enabled": bool(use_semantic),
        "semantic_available": bool(semantic_scores),
        "semantic_threshold": threshold,
    }
