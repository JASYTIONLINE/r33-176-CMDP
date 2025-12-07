# File Recovery Guide - Downloads Folder

## Situation
The `content/memos/downloads/` folder containing 22 .docx files (~1.3 MB) was accidentally deleted.

## Files That Were Lost
- 22 appointment memo .docx files
- Location: `F:\r33-176-CMDP\content\memos\downloads\`
- File types: .docx (Microsoft Word documents)

## Recovery Options (NO ADMIN PRIVILEGES REQUIRED)

### Option 1: PhotoRec (RECOMMENDED - Portable, No Admin Needed)
1. Download PhotoRec (portable, no installation): https://www.cgsecurity.org/wiki/PhotoRec
2. Extract the ZIP file to your Downloads folder (or anywhere you have write access)
3. Run `photorec_win.exe` (no installation needed!)
4. Select drive F: and press Enter
5. Choose partition type: Intel
6. Select file system: Other
7. Choose "Whole" to scan entire drive
8. Select a recovery destination on C: drive (NOT F: drive!)
9. Press 'File Opt' and enable .docx files
10. Press 's' to start recovery
11. Wait for scan to complete (may take 30-60 minutes)
12. Recovered files will be in the destination folder
13. Copy recovered .docx files back to `F:\r33-176-CMDP\content\memos\downloads\`

### Option 2: Wise Data Recovery Portable
1. Download from: https://portableapps.com/apps/utilities/wise-data-recovery-portable
2. Extract to Downloads folder
3. Run without installation
4. Scan F: drive for .docx files
5. Recover to C: drive first

### Option 2: PhotoRec (Command Line - More Advanced)
1. Download PhotoRec: https://www.cgsecurity.org/wiki/PhotoRec
2. Run PhotoRec
3. Select drive F:
4. Choose "Whole" or "Free" partition
5. Select file types: .docx
6. Choose recovery destination (NOT the same drive!)
7. Start recovery

### Option 3: Windows File Recovery (If Available)
Run in PowerShell as Administrator:
```powershell
winfr F: C: /n \content\memos\downloads\*.docx
```

## Important Notes
- **DO NOT** write new files to the F: drive until recovery is complete
- The longer you wait, the less likely recovery will succeed
- Recover to a DIFFERENT drive first (like C:), then copy back
- Stop using the computer for other tasks to avoid overwriting deleted files

## What We Found in OneDrive
Found related files in `C:\Users\jasyt\OneDrive\4000_military_files\cmdp\` but not the exact downloads folder. You may want to check if you have the original source files there.

## Next Steps
1. **IMMEDIATELY** download and run Recuva
2. Recover files to a safe location
3. Verify the files are intact
4. Copy them back to `F:\r33-176-CMDP\content\memos\downloads\`
5. Update .gitignore to ensure they're tracked in git going forward


