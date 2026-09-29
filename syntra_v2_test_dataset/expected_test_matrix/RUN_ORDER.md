# Syntra V2 Dataset Test Order

Run these in order after Syntra V2 is working:

1. TC01 Normal multimodal
2. TC02 Teacher correction/conflict
3. TC03 Visual-only
4. TC04 Blurry/rotated
5. TC05 Ambiguous handwriting
6. TC06 Missing audio
7. TC07 Missing visual
8. TC08 TXT-only
9. TC09 General-knowledge fallback
10. TC10 Queue + anonymous shared Q&A
11. TC11 Security/edge cases

For every test record:
- input files
- processing status transitions
- extracted evidence
- confidence values
- alignment relationships
- conflict status
- generated answer
- source badge
- evidence references
- UI behavior
- pass/fail
- unexpected behavior

IMPORTANT:
The MP3 files in this pack are synthetic audio signals paired with ground-truth transcript TXT files. They are useful for upload/queue/media-path testing, but should NOT be treated as a realistic speech-recognition quality benchmark. For a true ASR benchmark, add a real spoken recording separately.
