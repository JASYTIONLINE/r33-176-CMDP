# CMDP Equipment Status Report Class

This static HTML, CSS, and JavaScript class is integrated into the CMDP Compliance site. It opens on `esr/main/sl1-esr-key.html`, shows one slide image per page, and uses the site navigation to move between CMDP sections and ESR class slides.

## Folder Structure

- `esr/main/` - core slides (landing page `sl1-esr-key.html` plus linked narrative slides)
- `gcssa/` - GCSS-Army ESR access flow slides
- `references/` - end-of-class reference pages
- `../../assets/images/esr-class/slides/` - one slide image per page
- `css/` - shared presentation styling
- `js/` - shared navigation behavior

## Slide Flow

Open `esr/main/sl1-esr-key.html` from the CMDP site navigation to begin on slide 1. Use the top navigation to move between Home, Memos, SOPs, and slides 1-11.

## Replacing Slide Images

The current slide images are editable SVG files generated from the mock-up text. Replace files in `../../assets/images/esr-class/slides/` with final exported slide images using the same names, or update the matching HTML `src` paths if using a different file type.
