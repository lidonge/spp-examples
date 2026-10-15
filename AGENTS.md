# Public S++ project instructions

- Keep the book under `book/` publicly readable but reserved-rights. Do not apply MIT, Creative Commons or another open license to it. Demo and website code use the scoped MIT license in `LICENSE`.
- This repository owns the two current demos, book and website inputs. Do not copy compiler/runtime internals, credentials, original bank COBOL, private deployment data, database files or generated Java into it.
- Production demo business behavior must remain in SPP; APP/PHY declare realization. No handwritten business Java. Java tests may arrange input, compose generated services, assert results and inject technical faults.
- Preserve explicit participants, scenario/service boundaries, visible checks and transactions. Model names and enum codes are English; presentation defaults to en-US/USD, with optional Chinese catalogue bundles and preserved legacy bank currency rules.
- Format actual SPP/APP/PHY/enum source with four spaces and separate statements. Website rendering preserves those real line breaks.
- Generate `website/dist/` from `website/static/`, `book/en/` and `demos/`; never maintain the generated pages independently. Keep public URLs compatible when moving source files.
- State SDK requirements honestly. The Python-only website build can run without private compiler artifacts; generated-demo acceptance needs a supplied S++ SDK.
