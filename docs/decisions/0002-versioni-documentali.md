# ADR 0002 · Testi in Git e integrità verificata

- **Contesto** · Due originali da acquisire, con consultazione e conservazione delle versioni.
- **Alternative** · CMS, PDF solo, file Markdown non verificati.
- **Decisione** · Manifest JSON per lingua, hash SHA-256, versioni con URL stabili e parser costituzionale su CommonMark.
- **Motivazione** · Il repository conserva i sorgenti e rende ispezionabile la storia. Un unico sorgente alimenta testo completo e singoli articoli.
- **Compromessi** · Il parser deve essere verificato sul formato effettivo dei testi acquisiti. L’integrità dipende da un manifest attendibile.
- **Formulata da** · Codex. Revisione umana da registrare.
