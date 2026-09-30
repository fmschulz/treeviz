# Add metadata tracks

Use tracks to display a table beside the leaves: colors for groups, bars or
color scales for measurements, dots for presence, and text for descriptions.
Start with a loaded tree. For a worked dataset, use the
[first-tree tutorial](../tutorials/first-tree.md).

## Prepare and load your table

1. Put one leaf identifier in each row and one variable in each column. Use a
   single header row with distinct column names.
2. Save the sheet as **CSV UTF-8** or tab-separated text. TreeViz does not read
   `.xlsx` workbooks directly.
3. Click **Add Tree** in TreeViz and select the CSV or TSV while your tree is
   open, or drag the table onto the tree.
4. Choose the **Row key column** whose values match the imported leaf names.
   In the tutorial files, that column is `leaf_id` and its values are A–F.
5. To choose tracks yourself, leave **Goal prompt** empty and **Apply suggested
   tracks on import** unchecked.
6. Check the match counts in **Preview**, then click **Import**. If the counts
   are wrong, choose another row key or correct the identifiers in the file.

A row can appear anywhere in the table; its identifier determines the leaf it
matches. Leave missing cells empty. The [metadata reference](../METADATA.md)
lists file formats and [inferred column types](../METADATA.md#values-and-types).

## Choose a track

Open **Tracks**, click **+ Add Track**, select a **Column**, then select a
**Kind** and click **Add**. The menu shows the inferred column type in
parentheses and offers compatible kinds.

| What you want to show             | Example column                | Kind in the menu | Visible result                          |
| --------------------------------- | ----------------------------- | ---------------- | --------------------------------------- |
| Group membership                  | `habitat`: soil, water, gut   | **color-strip**  | One colored cell per leaf              |
| One measurement as color         | `abundance`: 12, 4, 8         | **gradient**     | A continuous color scale               |
| One measurement as length         | `abundance`: 12, 4, 8         | **bar**          | One bar per leaf                        |
| Several measurements side by side | `abundance`, `abundance_day2` | **heatmap**      | One cell per leaf and measurement       |
| Presence or absence               | `present`: yes, no            | **binary-dots**  | A dot for a true value                  |
| Descriptions                      | A column inferred as `text`   | **text**         | The table value written beside the leaf |

Binary columns also offer **color-strip**. Categorical columns offer
**color-strip**; numeric columns offer **gradient**, **bar**, and **heatmap**.

## Edit a track

1. In **Tracks**, click a track's title to expand its settings.
2. Set **Title** to the name you want readers to see in the legend.
3. Use **Column** to select the source field and **Palette** to choose colors
   where those settings are available.
4. Change **Width**, or **Cell width** for a heatmap, to give the values space.
5. Uncheck **Visible** to hide a track. Use its **Remove track** button to
   remove it while keeping the imported metadata.

A sequential palette such as **Viridis** suits an increasing measurement.
A diverging palette suits signed values with a meaningful center, such as
negative and positive effects. A categorical palette such as **Okabe-Ito**
keeps groups distinct.

Tracks appear in the order you add them, and saved sessions preserve that order.
The browser track panel has no reorder control.

For bars, enable **Show axis** so readers can interpret lengths. Adjust the
axis and helper-line controls in the expanded bar track.

## Add a two-column heatmap

With the tutorial metadata loaded:

1. Choose **+ Add Track**, **abundance (continuous)**, then **heatmap**.
2. Expand the heatmap track.
3. Under **Columns**, use **add column** to select **abundance_day2**.
4. Set **Title** to `Abundance by day` and choose **Viridis**.
5. Adjust **Cell width** if the cells are hard to see.

You should see two adjacent cells per leaf. F has a missing first-day cell and
a value of 6 on day two. Columns in one heatmap share a color scale, so compare
measurements with the same units. Use separate tracks for unrelated quantities.

Use the remove button beside a heatmap column to drop that column from the
track without removing it from the metadata table.

## Add a text track

The browser's **Kind** menu offers **text** only when the column is inferred as
`text`. A non-numeric column with at most 32 distinct values is usually
`categorical`, even if the values are names. The current import dialog has no
column-type override. The tutorial's six `display_name` values therefore do not
offer a text track.

To try a complete text example, save your current session first, then download
[text-track.nwk](../tutorials/data/text-track.nwk){ download="text-track.nwk" }
and [text-track.csv](../tutorials/data/text-track.csv){ download="text-track.csv" }.

1. Open the tree in a new TreeViz tab. If a **Replace tree** review appears,
   check **I understand** and click **Import**. Then import the CSV.
2. Choose **leaf_id** as the row key and check for **33 exact** matches.
3. Leave suggested tracks unchecked and click **Import**.
4. In **Tracks**, add **description (text)** with kind **text**.
5. Expand the track and increase its **Width** as needed.

Each leaf gets its description. This example has 33 distinct descriptions so
the browser infers `text`. For a small tree, [Rename leaf](labels.md#rename-one-leaf)
lets you change displayed names while preserving the session's metadata binding.

## Show legends and preserve the tracks

Click **Legend**, then click the star beside each section to include it in the
figure. The star's tooltip is **Display in figure**. Set each track's title
before exporting.

Choose **Export** → **Export Session (JSON)** to save the tree, metadata,
tracks, and settings together. A Newick file alone does not contain the tracks.

## Fix common import problems

- **No + Add Track button:** import a metadata table first. Loading a tree alone
  does not create metadata columns.
- **Wrong kinds in the menu:** inspect the column values and the type shown
  beside its name. `0/1` is inferred as numeric; use `yes/no` for presence dots.
  A unit suffix such as `12 kg` makes a value non-numeric. Put units in
  the header and keep numeric cells numeric.
- **Missing colors or bars:** check for unmatched leaves and empty cells.
  F's missing abundance in the tutorial is intentional.
- **Rows do not match:** open **Tracks** and use **Rebind leaves…** in its
  header to review normalization. To change the row-key column, import the
  table again; Rebind keeps the current row-key column.
- **A second table replaces the first:** combine columns into one CSV or TSV
  before importing. The session has one leaf-metadata table.
