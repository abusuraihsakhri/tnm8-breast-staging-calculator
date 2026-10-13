# TNM8 Breast Staging Calculator

An offline-capable **AJCC 8th-edition breast cancer anatomic stage-group reference**. Given established T, N and M categories, the application returns anatomical stage **0, IA–IIIC or IV**, using the NCI PDQ anatomical stage-group table.

**Scope:** This is **not** an AJCC 8 clinical or pathological *prognostic* stage calculator. Prognostic staging requires tumor grade, ER, PR, HER2 and sometimes additional information. Do not infer prognostic stage or treatment decisions from the anatomical result alone. Not independently validated for clinical deployment.

## Browser interface

The self-contained website is in [`web/index.html`](web/index.html). It needs no backend, package installation, account, or browser-Python runtime. Run it locally by opening the file or with:

```sh
python -m http.server 8001 --directory web
# Open http://localhost:8001
```

Choose primary tumor (T), regional nodes (N) and distant metastasis (M), then select **Calculate stage**. Unsupported combinations report an error rather than an invented stage. No identifiers are requested or sent to a server by the browser calculator.

## Python CLI

Python 3.10+ is supported. Anatomic staging uses only the standard library.

```sh
python tnm8_breast.py stage --t T2 --n N1mi --m M0
# anatomic_stage: IIB

python tnm8_breast.py stage-batch -i sample_tnm.csv -o staged.csv
```

Batch input must include `T,N,M` header columns; other columns are retained. Invalid rows stop processing with the line number, without writing a partial output file.

Python API:

```python
from staging import anatomic_stage
print(anatomic_stage("T1", "N0", "M0"))
```

Accepted prefixes `c`/`p`, selected T/N subcategories, `T1mi`, `N1mi`, and `M0(i+)` are normalized. Invalid `pM0`, unknown M0 groups, or post-neoadjuvant categories are rejected. M1 is stage IV regardless of the other categories.

## Optional FastAPI service

```sh
python -m pip install -r requirements.txt
python cli.py serve --host 127.0.0.1 --port 8000
```

The service serves the browser interface at `/` and offers `POST /api/stage`:

```sh
curl -X POST http://127.0.0.1:8000/api/stage \
  -H "Content-Type: application/json" \
  -d '{"t":"T2","n":"N1","m":"M0"}'
```

Swagger/OpenAPI documentation is available at `/docs` and `/openapi.json`.

Legacy modules (`cli.py audit`, `batch`, `chat`, `simulator.py`, `enrichment.py`, and `tnm8_breast.py single/batch`) are retained for compatibility. **Their synthetic numerical thresholds, scoring tiers, agent alerts and mock chat output are not AJCC staging, clinical risk predictions or validated medical advice.** The `sample.csv` file uses this separate legacy numerical format.

## Security and privacy

The static browser tool computes entirely client-side, with no third-party scripts or tracking. The server's legacy `/api/audit`, `/api/chat`, and `/api/audit/logs` endpoints require an `X-Admin-Token` header matching `API_ADMIN_TOKEN`. Configure a unique `AUDIT_SECRET_KEY` for stable HMAC audit signing, and `ALLOWED_HOSTS` for non-local deployment; see [`.env.example`](.env.example). Do not commit secret values.

The legacy regex-based PHI checks are **not complete de-identification or a HIPAA compliance guarantee**. The experimental service uses in-memory state and is not designed for real patient data or production clinical records. Do not expose it to the public internet without additional operational security and authentication controls.

## Tests and development

```sh
python -m pip install -r requirements.txt
python -m pytest -q
node --test web/staging.test.cjs
node --check web/app.js
```

GitHub Actions runs Python tests on 3.10–3.12 and JavaScript tests; on pushes to `master`, it attempts GitHub Pages publication from `web/`. Deployment depends on Pages being enabled and successful workflow permissions.

## References and limitations

- [NCI Breast Cancer Treatment (PDQ): AJCC Anatomical Stage Groups, Table 8](https://www.cancer.gov/types/breast/hp/breast-treatment-pdq)
- [AJCC cancer staging systems](https://www.facs.org/quality-programs/cancer-programs/american-joint-committee-on-cancer/version-9/)

This implementation provides group assignment from **known** TNM categories; it does not determine T or N from images, pathology, or clinical findings. It is not a substitute for the full AJCC staging manual, institutional guidance, or oncology/pathology review.

**License:** [MIT](LICENSE).
