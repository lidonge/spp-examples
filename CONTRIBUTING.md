# Contributing

Issues and small, focused pull requests are welcome. Include a concrete scenario, the relevant source file, expected behavior and observed behavior. Do not submit real customer data, credentials, proprietary bank source, compiled artifacts or database files.

## Demo and website code

Changes to demo and website code are contributed under the repository's MIT code license. Production demo business behavior belongs in SPP; APP/PHY describe realization. Do not add handwritten production business Java or edit generated output. Java tests may arrange participants, invoke generated services, assert outcomes and inject technical faults.

For source changes, preserve explicit participants, service boundaries, visible checks and transactions. Maintain English defaults and USD presentation. For formatting-only changes, check that lexical tokens are unchanged. Run relevant generated-service acceptance tests when the S++ SDK is available.

For website changes, rebuild with `website/build_book.py`, run `website/check_site.py`, and check desktop/mobile reading and source line numbers. Source code displays its actual line breaks; do not enable browser automatic wrapping as a substitute for formatting the source files.

## Book corrections

The book is publicly readable but is not MIT-licensed or Creative Commons licensed. Its terms are in `book/COPYRIGHT.md`. Report corrections in an issue; do not assume that submitting an issue or code pull request grants rights to the book. Obtain written agreement before submitting substantive replacement manuscript content or translations. Existing rights and applicable-law permissions remain unchanged.

The maintainer reviews and releases changes. The public website is generated from this repository; do not edit the live server as a separate source of truth.
