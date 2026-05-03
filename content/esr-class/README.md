# CMDP Equipment Status Report Class

This static HTML, CSS, and JavaScript class is integrated into the CMDP Compliance site. It opens on `equipment-status-report-class.html`, shows one slide image per page, and uses the site navigation to move between CMDP sections and ESR class slides.

## Folder Structure

- `equipment-status-report-class.html` - ESR class landing page and first slide
- `content/` - slide pages 2 through 11
- `../../assets/images/esr-class/slides/` - one slide image per page
- `css/` - shared presentation styling
- `js/` - shared navigation behavior

## Slide Flow

Open `equipment-status-report-class.html` from the CMDP site navigation to begin on slide 1. Use the top navigation to move between Home, Memos, SOPs, and slides 1-11.

## Replacing Slide Images

The current slide images are editable SVG files generated from the mock-up text. Replace files in `../../assets/images/esr-class/slides/` with final exported slide images using the same names, or update the matching HTML `src` paths if using a different file type.
