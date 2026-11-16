# Data provenance, preparation, and labeling

## Category classification: BANKING77

Source: [PolyAI task-specific datasets](https://github.com/PolyAI-LDN/task-specific-datasets/tree/master/banking_data).
Paper: [Casanueva et al., Efficient Intent Detection with Dual Sentence Encoders (2020)](https://arxiv.org/abs/2003.04807).
The upstream repository describes online banking queries with 77 annotated intents,
10,003 training examples, and 3,080 test examples. Its dataset license is CC BY 4.0;
retain attribution when redistributing derived data. Raw records are downloaded locally,
not committed to this repository.

Pinned source revision: `57ec275d8078af65b7731c2a98be812d844a6d6b`.

SupportPilot maps intents to **billing, technical, account, general** through the explicit
sets in `backend/ml/taxonomy.py`. The remaining intents are general inquiries. For example,
`transaction_charged_twice` maps to billing, `card_not_working` to technical,
`passcode_forgotten` to account, and `card_arrival` to general. These are operational
groupings defined for this application, not original four-class ground truth.
The complete 77-intent mapping and source checksums are in the generated evaluation report.

```powershell
# From backend/, with the environment active
python -m ml.prepare_banking --revision 57ec275d8078af65b7731c2a98be812d844a6d6b
python -m ml.train --task category --data-dir data/category
```

Preparation uses Pandas for schema validation and missing-value handling, normalizes text
for duplicate detection, removes conflicting duplicate labels within each split, and
removes normalized overlaps from training against the held-out test set. The original
test membership is retained. Audit counts and SHA256 fingerprints are recorded.

The pipeline fits word/character TF-IDF features **only on training text** and trains
class-balanced logistic regression. Fixed hyperparameters and seed 42 avoid test-driven
selection. Evaluation reports accuracy, macro precision/recall/F1, per-class scores,
confusion counts, sample sizes, class distributions, majority baseline accuracy,
library versions, and provenance. NumPy supports probability selection and baseline input.

Only exact normalized duplicates are excluded; paraphrases or shared entities may remain.
Source data does not provide customer/thread group IDs. The banking results therefore
do not establish performance on general SaaS support tickets. Validate on independently
labeled business-specific data before relying on predictions.

## Priority: reviewed labels required

No suitably verified real human-labeled customer-support priority dataset is bundled.
Public examples can be synthetic, weakly labeled, or have unclear provenance. Rather than
present those as real operational priority data, the priority service reports `untrained`.
The pipeline and endpoint are implemented and become usable once a reviewed dataset is supplied.

Prepare a UTF-8 CSV with these columns:

| Column | Requirement |
|---|---|
| `text` | Subject + description available at ticket intake; remove private identifiers |
| `priority` | Human-reviewed `low`, `medium`, or `high` |
| `group_id` | Stable pseudonymous customer/thread/incident identifier |

Use [examples/priority-labeling-template.csv](../examples/priority-labeling-template.csv)
as a schema reference. Its single unlabeled fictional row is not a training dataset.

### Suggested review process

1. Obtain permission to use/export a real ticket collection. Record source, license/consent,
   collection dates, domain, label policy, and known restrictions.
2. Use only intake text. Exclude agent replies, resolution, SLA breach, close time,
   satisfaction, existing priority tags, or other post-outcome fields from predictors.
3. Define business-specific impact/urgency criteria before reviewing examples:
   high = significant business blockage/security-impact requiring prompt specialist review;
   medium = degraded service with a workaround; low = information or non-blocking request.
   These are annotation guidelines, not automated keyword labels or SLA promises.
4. Have two reviewers label independently, measure agreement, adjudicate disagreements,
   and record the process. Existing organization labels can be used after policy validation.
5. Assign the same group ID to related customer threads or incidents; use connected groups
   if multiple identifiers link records. Do not include group IDs in model input.
6. Prepare once and keep the test partition frozen. For later model selection, use a
   validation split from training only. Prefer temporal validation for changing live queues.

```powershell
python -m ml.prepare_priority --input reviewed.csv --source "Approved source and collection dates" --license "Documented permission"
python -m ml.train --task priority --data-dir data/priority
```

A stable SHA256 hash partitions groups approximately 80/20. Exact text deduplication
and group-disjointness are checked. At least five training and two test rows per class
are required as a minimal smoke-check safeguard; those counts are insufficient for a
credible production benchmark. Collect a substantially larger representative dataset.
The code does not verify your licensing or annotation claims automatically.

## Sentiment model

[Cardiff NLP Twitter RoBERTa sentiment](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest)
is an English three-class pretrained model: negative, neutral, positive. The model card
lists CC BY 4.0 and the TimeLMs/TweetNLP references. It was trained for social-media text,
not this application's support tickets. SupportPilot uses PyTorch in evaluation/inference
mode and truncates inputs to 512 tokens. Scores are softmax outputs, not calibrated certainty.
No support-domain sentiment accuracy or fine-tuning claim is made.

The pinned revision `3216a57f2a0d9c45a2e6c20157c20c49fb4bf9c7` publishes PyTorch `.bin`
weights. The downloader uses PyTorch >=2.6 weights-only loading, trusts no remote model
code, and saves a local safetensors copy plus provenance. Inference does not contact
Hugging Face; first-time model downloads require internet access.

## Demo content and reports

`app.seed` creates explicitly fictional customers and messages with `.test` email addresses.
Its manual routing labels are not model results. Unit-test fixtures are also constructed
test data and are never mixed with the BANKING77 benchmark. Only the actual training CLI
writes portfolio evaluation reports under `backend/reports/`.
