The pack includes:

Test	Input	What it checks
TC01	Audio + image + transcript	Normal multimodal fusion
TC02	Audio + conflicting slide	Teacher correction + conflict
TC03	Image only	Visual-only evidence
TC04	Blurry + rotated image	Low-confidence visual handling
TC05	Ambiguous handwriting	Uncertainty handling
TC06	Image without audio	Missing-audio degradation
TC07	Audio without visual	Missing-visual degradation
TC08	TXT	TXT transcript/notes processing
TC09	Out-of-scope question	General-knowledge fallback
TC10	3 simultaneous questions	Queue + user isolation + anonymity
TC11	Empty/unsupported/Unicode files	Security and edge cases

One important detail: the included MP3s are synthetic audio signals, paired with ground-truth transcript files. They're useful for testing upload/storage/queue/media-processing paths, but not for judging speech-recognition accuracy. For that, add a real spoken recording later.

Gemini officially supports multimodal inputs including audio, images and documents, and its current documentation describes timestamped audio understanding and PDF/document processing.

How to test Syntra V2 — exact order
STEP 1 — Start Syntra V2

First make sure Antigravity has completed enough of the application to support:

Authentication
PostgreSQL
Den creation
Rock creation
Material upload
Background jobs
Gemini processing
Q&A
Evidence viewer

Start the application normally.

Do not manually insert these datasets into PostgreSQL.

Upload them through Syntra's actual UI.

STEP 2 — Create a real test account

Create:

Email: your-test-email
Password: your-test-password

Then create a Den:

Den Name:
Syntra Multimodal Testing

Description:
Testing multimodal evidence, alignment, conflicts and Q&A.

You automatically become:

DEN ADMIN
STEP 3 — Create Rocks

Create:

Rock 1
Title: Normal Multimodal

Rock 2
Title: Conflict Testing

Rock 3
Title: Visual Understanding

Rock 4
Title: Uncertainty Testing

Rock 5
Title: Missing Modality

Rock 6
Title: Text and Knowledge

Rock 7
Title: Queue Testing

This lets you keep your test material organized.

STEP 4 — Test TC01 first

Open:

01_normal_multimodal/

You will find:

slide_01.png
lecture.mp3
transcript.txt
README.txt

Upload:

lecture.mp3
slide_01.png
transcript.txt

through the normal Admin material upload workflow.

Don't manually tell Syntra what the files contain.

Let Syntra discover it.

You want to see something like:

UPLOAD
   ↓
VALIDATING
   ↓
QUEUED
   ↓
EXTRACTING
   ↓
ALIGNING
   ↓
FUSING
   ↓
COMPLETED
STEP 5 — Inspect the extracted evidence

After processing, open the evidence viewer.

You should find evidence resembling:

Audio
00:08–00:16

"The input data first enters the processing node."
Visual
Input Data
     ↓
Processing Node
     ↓
Output

Then Syntra should create a relationship such as:

Audio Evidence
      ↓
   ELABORATES
      ↓
Visual Evidence

The exact wording may differ because Gemini is generating the extraction, but the relationship and provenance should exist.

STEP 6 — Test Q&A

Ask:

What does the processing node do?

Expected behavior:

ANSWER

The processing node validates and transforms
the input data before it becomes the output.

SOURCE
DEN MATERIAL

Then open:

View Evidence

You should be able to trace the answer back to:

Audio timestamp
+
Slide/image

This is one of the most important Syntra demonstrations.

STEP 7 — Test cross-modal Q&A

Ask:

What did the teacher say about the processing node shown in the diagram?

Syntra should retrieve both:

VISUAL
+
AUDIO

The answer should not simply describe the image.

It should connect:

WHAT IS SHOWN
       +
WHAT THE TEACHER SAID

Then the Evidence Viewer should expose the supporting sources.

STEP 8 — Test TC02 — teacher correction

Now open:

02_teacher_correction/

Upload:

slide_02.png
lecture.mp3
transcript.txt

The slide says:

Default HTTP port: 80

But the teacher says:

Ignore that value for this lecture; it is a typo.

For our example, use port 8080.

This is an extremely important test.

Syntra should detect:

CONFLICT

and preferably:

EXPLICIT_CORRECTION

because the teacher explicitly corrected the slide.

STEP 9 — Check Admin notification

Go to:

Notifications

The Den Admin should receive something similar to:

⚠ Conflict detected

A lecture source and visual source contain
conflicting information.

Review required.

Open it.

You should see something like:

SOURCE A
Slide
Port 80

SOURCE B
Teacher audio
Port 8080

STATUS
Explicit correction
STEP 10 — Resolve the conflict

Admin should be able to enter:

Correction:

For this lecture context, use port 8080.

Save it.

Now verify:

Original slide

Still says:

80
Original audio/transcript

Still says:

8080
Admin resolution

Contains:

8080

This is critical.

Syntra must not rewrite the original slide to 8080.

That would destroy provenance.

STEP 11 — Test TC03 — visual-only

Open:

03_visual_only/

Upload:

diagram.png

No audio.

Ask:

Which layer is shown between Application and Network?

Expected:

Transport

But the source should be:

SOURCE
DEN MATERIAL

MODALITY
VISUAL

It should not say:

The teacher explained that...

because there is no teacher audio.

This tests:

visual-only knowledge extraction.

STEP 12 — Test TC04 — blurry + rotated

Open:

04_blurry_rotated/

Upload:

board_photo.png

This image is intentionally:

rotated
blurred

Syntra should NOT confidently manufacture information.

You want to see something like:

Confidence: LOW

or:

Uncertain visual evidence

If the system cannot confidently read something, it should say so.

Bad behavior
The board definitely says X.

when X isn't readable.

Good behavior
The visual evidence appears to contain
"Merge Sort", but portions of the image are
unclear. Confidence: LOW.
STEP 13 — Test TC05 — handwriting

Open:

05_handwriting_ambiguous/

Upload:

handwritten_notes.png

Ask:

What does the handwritten push(?) note mean?

The important thing isn't whether Gemini guesses the handwriting correctly.

The important thing is whether Syntra recognizes:

UNCERTAINTY

You should see:

Confidence: LOW

or:

Unable to confidently interpret handwriting.

This is exactly the kind of adversarial behavior you want to demonstrate.

STEP 14 — Test TC06 — remove audio

Open:

06_missing_audio/

Upload only:

slide_03.png

Then ask:

What did the teacher say about binary search?

Expected:

Audio evidence is unavailable, so I cannot
verify what the teacher said.

Not:

The teacher said...

because there is no audio.

Now ask:

What does the slide say about binary search?

That should work from the visual source.

This demonstrates graceful degradation.

STEP 15 — Test TC07 — remove visual

Open:

07_missing_visual/

Upload:

lecture.mp3
transcript.txt

Then ask:

What did the teacher say about the diagram?

Syntra can answer from audio/transcript evidence.

But it should clearly indicate:

Visual source unavailable.

This proves Syntra doesn't assume that every modality exists.

STEP 16 — Test TC08 — TXT input

Open:

08_txt_only/

Upload:

lecture_notes.txt

Ask:

What is Round Robin scheduling?

Expected source:

DEN MATERIAL

Evidence:

TXT

This tests the additional TXT input you specifically wanted for Syntra V2.

STEP 17 — Test TC09 — general knowledge

This one is important.

Upload:

09_general_knowledge_fallback/scope.txt

Then ask:

What is the Chandrasekhar limit?

The Den doesn't contain this information.

Syntra may answer from general knowledge.

But the UI must clearly say:

GENERAL KNOWLEDGE

This concept was not found in this Den's
materials. The following answer is based
on general knowledge.

It must not pretend:

According to your lecture...

This tests your Den-material vs general-knowledge distinction.

STEP 18 — Test TC10 — multiple users

Now create three test accounts.

For example:

User A
User B
User C

Put all three into the same Den.

Use:

10_multi_user_queue/queue_test.json

Submit these quickly:

User A

What does the processing node do?

User B

What is the output in the pipeline?

User C

Does the slide agree with the transcript?

You should see:

Q1 → QUEUED
Q2 → QUEUED
Q3 → QUEUED

Then:

Q1 → PROCESSING
Q2 → PROCESSING
Q3 → PROCESSING

Eventually:

Q1 → COMPLETED
Q2 → COMPLETED
Q3 → COMPLETED
STEP 19 — Check the most important anonymity requirement

Go to the shared Q&A feed.

STEP 20 — Test Q&A isolation

This is another very important test.

Ask completely different questions from different accounts.

For example:

User A:
What does the processing node do?

User B:
What is the output?

User C:
Does the teacher correct the slide?

Check every answer.

There must be zero context mixing.

For example, User B's answer must not accidentally contain:

According to User A's question...

or evidence retrieved specifically for another thread.

STEP 21 — Test follow-up

Ask:

What does the processing node do?

Then:

Why is it needed?

The second question should understand the first question's thread context.

But if another user asks:

Why is it needed?

their question should not automatically inherit someone else's thread.

This tests:

THREAD A
  Q1
  Q2

THREAD B
  Q1

rather than one giant global conversation.
