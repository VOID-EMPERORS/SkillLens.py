# SkillLens — Advanced Resume Skill Gap Analyzer

SkillLens is a Python + Streamlit mini-project that compares a resume with a job description. It combines transparent skill-keyword matching with optional semantic similarity, then presents matched skills, potential gaps, learning suggestions, charts, and a downloadable PDF report.

> Educational project: its score is an estimate of detected skill coverage, not a hiring prediction or a complete assessment of a person's abilities.

## Features

- Upload PDF and TXT resumes.
- Paste a job or internship description.
- Detect supported skills from a curated skill/alias dictionary.
- Optional semantic similarity using `sentence-transformers/all-MiniLM-L6-v2`.
- Chunk resume text to compare each required skill against short sections rather than one long document.
- Show overall fit score, skill coverage chart, match method, and similarity score.
- Recommend next steps and learning resources for skill gaps.
- Download a PDF report.
- Runs locally; no paid AI API key is required.

## Technology stack

- Python 3.11+
- Streamlit
- PyMuPDF
- Pandas
- Plotly
- ReportLab
- Sentence Transformers and PyTorch (optional semantic model)

## Folder structure

```text
resume-skill-gap-analyzer-advanced/
├── app.py
├── analyzer.py
├── recommendations.py
├── report_generator.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Windows setup

### 1. Install Python

Install Python 3.11 or newer from https://www.python.org/downloads/ . If available, enable **Add Python to PATH** in the installer.

Check installation in PowerShell:

```powershell
python --version
pip --version
```

### 2. Open the project directory

Extract the downloaded ZIP, then open PowerShell in the extracted folder.

### 3. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, skip activation and use the virtual environment's Python executable directly as shown below.

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

PyTorch and Sentence Transformers can be large downloads. Semantic mode may download the `all-MiniLM-L6-v2` model on first use and needs internet access for that initial download. Model caching is handled by the installed libraries.

If you want the lightweight keyword-only version, install the core dependencies without the final two requirements:

```powershell
pip install streamlit pymupdf pandas plotly reportlab
```

Then switch off **Use semantic similarity** in the sidebar.

### 5. Run the application

```powershell
python -m streamlit run app.py
```

Open the local URL printed in the terminal, usually `http://localhost:8501`.

To stop the app, press `Ctrl+C` in PowerShell.

## How to use

1. Upload a text-based PDF or TXT resume.
2. Enter a role title if desired.
3. Paste the job description.
4. Choose whether to use semantic similarity and set the threshold.
5. Click **Analyze resume fit**.
6. Review the Overview, Skill evidence, Learning plan, and Export report tabs.

## How the analysis works

### 1. Explicit skill extraction

`analyzer.py` maintains canonical skill names and aliases. For example, `Postgres` maps to `PostgreSQL`, and `scikit learn` maps to `Scikit-learn`.

### 2. Semantic similarity

When enabled and installed, Sentence Transformers embeds short chunks of resume text and a phrase for each required skill. The highest cosine similarity for a skill is compared with the selected threshold. A score above the threshold can count as a semantic match even if the exact skill keyword is not present.

Semantic similarity can produce false positives. A related phrase is not proof of actual experience, so review the evidence table before using the results. The first model run may take time while the model downloads and loads.

### 3. Fit score

```text
Fit score = matched supported job skills / all supported job skills × 100
```

The score counts both explicit and accepted semantic matches equally. It does not account for skill importance, proficiency, years of experience, project quality, or hiring context.

## Privacy notes

- The code does not send resume content to a hosted AI API.
- The semantic model is downloaded from the model hub on first use if it is not already cached. Resume text is embedded locally by the installed model.
- If you deploy the app publicly, review the hosting provider's logging, storage, and access controls before accepting real resumes.
- Use synthetic or redacted data for class demonstrations.

## Limitations

- Scanned/image-only PDFs are not OCR-processed.
- Only skills in `SKILL_ALIASES` are recognized explicitly.
- Semantic similarity is approximate and may infer relationships incorrectly.
- Very long or unusually formatted resumes may need better text extraction.
- The tool should not be used as the sole basis for hiring or career decisions.

## Customization

- Add aliases and canonical skills in `analyzer.py`.
- Add learning recommendations in `recommendations.py`.
- Adjust the interface and charts in `app.py`.
- Change the semantic threshold in the sidebar.

## GitHub upload

Create an empty repository on GitHub, then run these commands in the project folder:

```powershell
git init
git add .
git commit -m "Build advanced SkillLens resume analyzer"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/resume-skill-gap-analyzer-advanced.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. Install Git first if PowerShell cannot find the `git` command.

## Possible future improvements

- Add OCR for scanned resumes.
- Weight essential skills more heavily than optional skills.
- Extract experience, education, projects, and certifications into separate sections.
- Add unit tests and a small synthetic test dataset.
- Add a user-editable skills taxonomy and explainable evidence snippets.
- Add a deployment workflow with clear privacy controls.

## License

For educational use. Add a license file if you intend to publish or redistribute the project under a specific open-source license.
