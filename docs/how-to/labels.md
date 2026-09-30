# Edit labels

Use a leaf label to name one tip, a clade annotation to name a group, or a text
track to display a metadata column beside the tree.

## Rename one leaf

1. Right-click a leaf label or its node.
2. Choose **Rename leaf**.
3. Type the new text and press **Enter**. Press **Escape** to cancel.

For example, rename **A** to `Sample A` in the
[first-tree tutorial](../tutorials/first-tree.md). Clicking elsewhere cancels
an unfinished edit.

Renaming preserves the leaf's metadata binding within the session. TreeViz
retains the original imported identifier for later matching. Save
`.treeviz.json` to preserve that relationship. If you export a renamed Newick
tree for another tool, check that tool's expected leaf identifiers.

## Change the appearance of leaf labels

For all leaf labels, open **Controls** → **Labels** and set the font and size.
**Show labels** controls visibility. **Auto-cull overlaps** hides labels that
would overlap; zooming in brings them back as room becomes available.

For one leaf, double-click its label or node to open **Inspector**, then adjust
**Label color** or **Label size**.

For a group, right-click the ancestor's node and choose **Style clade**. Use
**Label color** and **Label style** to format its descendant leaf labels. See
[Select the clade](style-clades.md#select-the-clade) before applying a group edit.

## Add a group name

Right-click the group's internal node, choose **Annotate clade…**, type a name,
and press **Enter**. Drag the annotation to place it. Use **Style clade** →
**Clade annotation** for its color, bold style, and size.

A group annotation does not rename its leaves. The same annotation can label
the wedge when you collapse that clade. The [clade guide](style-clades.md)
walks through an example with leaves C, D, E, and F.

## Display descriptions from metadata

Import a table whose row keys match the leaves and add a **text** track from a
column inferred as `text`. That writes an additional label beside each leaf;
it does not replace the imported leaf name.

For columns with only a few distinct names, the browser infers `categorical`
and does not offer **text** in **Add Track**. See the
[text-track example](metadata-tracks.md#add-a-text-track) for the current limit
and downloadable data.

## Make crowded labels readable

1. Click **Fit**, then zoom into the region you need to inspect.
2. Check **Show labels** in **Controls**. If **Auto-cull overlaps** is enabled,
   some labels will disappear at a distant zoom.
3. In **Rect**, choose **Label** above the tree to align names in a column.
4. Adjust label size and **Controls** → **Branches & nodes** → **Branch spacing**
   to separate rows.
5. For many closely related tips, [collapse their clade](style-clades.md#collapse-a-clade-into-a-wedge)
   and use one group annotation.

Save the final positions and styling with **Export Session (JSON)**. Check the
exported figure at the size at which someone will read it.
