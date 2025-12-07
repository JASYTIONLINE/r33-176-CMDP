# Bloat Analysis Report

## Summary
Found **~3.4 MB** of unnecessary files and folders that are not needed for the website build.

## Detailed Findings

### 1. `quartz/docs/` - **~2.1 MB (91 files)**
- **Status**: BLOAT - Not needed for builds
- **Description**: Documentation for the Quartz framework itself
- **Impact**: Takes up space but doesn't affect build process
- **Note**: Part of git submodule, will be restored on submodule update

### 2. `quartz/.github/` - **~11 KB (9 files)**
- **Status**: BLOAT - Not needed for builds
- **Description**: GitHub workflows, issue templates, and PR templates for the Quartz project
- **Files**:
  - `dependabot.yml`
  - `FUNDING.yml`
  - `ISSUE_TEMPLATE/` (bug_report.md, feature_request.md)
  - `pull_request_template.md`
  - `workflows/` (build-preview.yaml, ci.yaml, deploy-preview.yaml, docker-build-push.yaml)
- **Impact**: Minimal space, but completely unused
- **Note**: Part of git submodule, will be restored on submodule update

### 3. `quartz/content/` - **Empty folder**
- **Status**: BLOAT - Not needed
- **Description**: Empty folder in quartz submodule
- **Note**: Your workflow copies from root `content/` to `quartz/content/`, so this folder is overwritten anyway

### 4. `content/memos/downloads/` - **~1.3 MB (22 .docx files)**
- **Status**: BLOAT - Source files, not needed for website
- **Description**: Original Word documents that are already converted to Markdown
- **Impact**: Already ignored by `.gitignore`, but taking up local disk space
- **Recommendation**: Can be safely deleted if you have the source files backed up elsewhere

### 5. `content/excel/` - **Empty folder**
- **Status**: BLOAT - Not needed
- **Description**: Empty folder with no files

## What IS Needed

The build process only requires:
- `quartz/quartz/` - The actual Quartz framework code
- `quartz/package.json` and `quartz/package-lock.json` - Dependencies
- `quartz.config.ts` and `quartz.layout.ts` - Your configuration
- `content/` - Your markdown content (excluding downloads/)

## Recommendations

### For Submodule Bloat (`quartz/docs/`, `quartz/.github/`, `quartz/content/`)
Since `quartz` is a git submodule, you have limited options:

1. **Accept it** - These files are part of the Quartz repository and will be restored on updates
2. **Use sparse-checkout** - Configure git to only checkout needed parts of the submodule
3. **Switch to npm package** - If Quartz is available as an npm package, use that instead

### For Local Bloat
1. **Delete `content/memos/downloads/`** - Safe to remove if you have backups
2. **Delete `content/excel/`** - Empty folder, safe to remove

## Total Bloat
- **Submodule bloat**: ~2.1 MB (docs + .github)
- **Local bloat**: ~1.3 MB (downloads folder)
- **Total**: ~3.4 MB


