# Beauty catalog intelligence

A three-page Power BI portfolio project using the supplied skincare catalog. Palette: warm ivory, sand, caramel and espresso. Pages cover catalog composition, ingredient reach and data quality.

The beauty redesign uses a left navigation rail, rounded ivory panels, icon-led KPI cards and italic Georgia headings, inspired by the supplied [Master UI reference](https://bibb.pro/products/power-bi-master-ui-template/). The artwork and skincare icons are drawn locally for this project. Product-detail icons are decorative bottle glyphs, not product classifications.

## Open the report

Open **`Beauty_Studio_Final.pbix`** for the final three-page report. This is the single finished file to use and share.

For the editable project:

1. Open `Beauty_Studio/Beauty_Studio.pbip` in a recent Power BI Desktop for the latest beauty redesign (`PowerBI/Beauty.pbip` is the working project).
2. Click **Home → Refresh** to load the embedded cleaned snapshots. No server, account or external data path is required.
3. Use **File → Save as** and choose **Power BI files (*.pbix)** to create `Beauty_Catalog.pbix`.

If your version asks to enable Power BI Project support, enable the relevant preview feature and restart Desktop. Project support varies by Desktop version. This is a PBIP project, not a renamed PBIX.

## Data and interpretation

The original `Data/beauty_data.jsonl` contains 1,000 products and 17,442 ingredient entries. The existing source CSV contains no usable records; it was not overwritten. The source has no timestamps, price, transactions or clinical outcomes. Catalog tags do not prove clinical suitability, and missing tags do not establish ingredient presence.

The cleaning script normalizes Unicode, removes invisible characters, collapses whitespace, preserves missing numeric values, and exports typed tables. Ingredient aliases are not merged. Repeated product names and repeated ingredient occurrences remain traceable. See `cleaning_audit.json`, `cleaned/review_queue.csv`, and `../scripts/build_portfolio.py`.

## Model and interactions

`Products` has one row per source product ID. `Ingredient occurrences` has one row per product / source ingredient position. `Ingredients` has one row per normalized ingredient name. `Product functions` has one row per product / function. Single-direction relationships keep product filters consistent without multiplying product counts. `Quality checks` is a disconnected full-snapshot audit table.

The overview supports brand and fragrance-tag slicing. Ingredient reach counts distinct products; the ingredient slicer affects ingredient reach only. Function reach follows product/brand selections. Quality findings remain full-snapshot while product cards and detail respond to selection. Top-rank charts may display more than 10 or 12 items when ranks tie.

The report uses native Power BI interactions. It does not contain custom animated visuals; CSS-style entrance animation is not implemented in this deliverable. There is no genuine time field for a play-axis animation. Cross-filtering and selection provide interactive exploration.

## Home layout update

The overview is now **Home**. The breadcrumb text is hidden, all slicers sit in the header, and sidebar navigation uses product-related cream-jar, dropper and beauty-mirror icons. Home compares brands with a bar chart, formula-size groups with stacked columns, alcohol-free tags with a donut and product counts by ingredient count with a line chart. The line's horizontal axis is ingredient count; it is not a time series. The ingredient explorer adds a stacked source-rating breakdown in the former bottom filter area.

A calendar slicer requires a genuine date field and its business meaning. No dates were invented or inferred from filesystem timestamps. The calendar request remains pending a dated source or the user's choice to omit it.

## Reproduce

Run `python scripts/build_portfolio.py` from the repository root. This regenerates the cleaned CSVs and the PBIP from the original JSONL. The model embeds compressed cleaned snapshots; refreshing Desktop reloads these snapshots. To incorporate edited raw input, rerun the pipeline before reopening the project. Rebuilding regenerates visual definitions and overwrites the generated project; save your own design edits separately first.

After rebuilding, run `python scripts/restyle_beauty.py` with Pillow installed to reapply the beauty design. The script keeps analytical bindings and adds the three background artwork files, navigation actions, italic titles and a decorative product-image column. `before_beauty_restyle.zip` preserves the preceding project version. In Desktop editing mode, use Ctrl+click on sidebar navigation buttons.

Report definitions are checked against Microsoft's public PBIR JSON schemas with `scripts/validate_project.py` (requires jsonschema). Source row counts and foreign keys are checked during the build. Desktop render validation is recorded separately in `verification.md`.

## CV description

**Skincare catalog analytics | Power BI, DAX, Power Query, Python**  
Cleaned and modeled 1,000 products and 17,442 ingredient entries; built an interactive three-page Power BI report with brand exploration, distinct-product ingredient reach and a traceable data-quality audit.

## References

- [Microsoft: Power BI Desktop projects](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)
- [Microsoft: Enhanced report format](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report)
