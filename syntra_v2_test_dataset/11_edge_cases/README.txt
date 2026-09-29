Edge cases:
1. empty.txt -> reject or handle gracefully.
2. unsupported.exe -> reject safely.
3. very long/unusual filename -> safe storage name, no path traversal.
4. unicode_notes.txt -> preserve Unicode.
5. Try a duplicated upload -> checksum/version behavior should be predictable.
6. Try unauthorized access to another Den's material -> deny server-side.
