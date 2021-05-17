---
id: settings_project_global
title: Project Global Setting
sidebar_label: Global
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Project settings can have project specific values. Each new project is using studio values defined in **default** project but these values can be modified or overriden per project.

:::warning Default studio values
Projects always use default project values unless they have [project override](../admin_settings#project-overrides) (orage colour). Any changes in default project may affect all existing projects.
:::

## Profile filters

Many of the settings are using a concept of **Profile filters**

You can define multiple profiles to choose from for different contexts. Each filter is evaluated and a 
profile with filters matching the current context the most, is used. 

You can define profile without any filters and use it as **default**. 

Only **one or none** profile will be returned per context.

All context filters are lists which may contain strings or Regular expressions (RegEx).
- **`hosts`** - Host from which publishing was triggered. `["maya", "nuke"]`
- **`families`** - Main family of processed subset. `["plate", "model"]`
- **`tasks`** - Currently processed task. `["modeling", "animation"]`

:::important Filtering
Filters are optional. In case when multiple profiles match current context, profile with higher number of matched filters has higher priority that profile without filters.
(Eg. order of when filter is added doesn't matter, only the precision of matching does.)
:::

## Publish plugins

Publish plugins used across all integrations.


### Extract Review
Plugin responsible for automatic FFmpeg conversion to variety of formats.

Extract review is using [profile filtering](#profile-filters) to be able render different outputs for different situations.

Applicable context filters:
 **`hosts`** - Host from which publishing was triggered. `["maya", "nuke"]`
- **`families`** - Main family of processed subset. `["plate", "model"]`

![global_extract_review_profiles](assets/global_extract_review_profiles.png)

**Output Definitions**

Profile may generate multiple outputs from a single input. Each output must define unique name and output extension (use the extension without a dot e.g. **mp4**). All other settings of output definition are optional.

![global_extract_review_output_defs](assets/global_extract_review_output_defs.png)
- **`Tags`**
    Define what will happen to output.

- **`FFmpeg arguments`**
    These arguments are appended to ffmpeg arguments auto generated by publish plugin. Some of arguments are handled automatically like rescaling or letterboxes.
    - **Video filters** additional FFmpeg filters that would be defined in `-filter:v` or `-vf` command line arguments.
    - **Audio filters** additional FFmpeg filters that would be defined in `-filter:a` or `-af` command line arguments.
    - **Input arguments** input definition arguments of video or image sequence - this setting has limitations as you have to know what is input.
    - **Output arguments** other FFmpeg output arguments like codec definition.

- **`Output width`** and **`Output height`**
    - it is possible to rescale output to specified resolution and keep aspect ratio.
    - If value is set to 0, source resolution will be used.

- **`Letter Box`**
    - **Enabled** - Enable letter boxes
    - **Ratio** - Ratio of letter boxes
    - **Type** - **Letterbox** (horizontal bars) or **Pillarbox** (vertical bars)
    - **Fill color** - Fill color of boxes (RGBA: 0-255)
    - **Line Thickness** - Line thickness on the edge of box (set to `0` to turn off)
    - **Fill color** - Line color on the edge of box (RGBA: 0-255)
    - **Example**

    ![global_extract_review_letter_box_settings](assets/global_extract_review_letter_box_settings.png)
    ![global_extract_review_letter_box](assets/global_extract_review_letter_box.png)

### IntegrateAssetNew

Saves information for all published subsets into DB, published assets are available for other hosts, tools and tasks after.
#### Template name profiles

Allows to select [anatomy template](admin_settings_project_anatomy.md#templates) based on context of subset being published. 

For example for `render` profile you might want to publish and store assets in different location (based on anatomy setting) then for `publish` profile.
[Profile filtering](#profile-filters) is used to select between appropriate template for each context of published subsets.

Applicable context filters:
- **`hosts`** - Host from which publishing was triggered. `["maya", "nuke"]`
- **`tasks`** - Current task. `["modeling", "animation"]`

    ![global_integrate_new_template_name_profile](assets/global_integrate_new_template_name_profile.png)
    
(This image shows use case where `render` anatomy template is used for subsets of families ['review, 'render', 'prerender'], `publish` template is chosen for all other.)

#### Subset grouping profiles

Published subsets might be grouped together for cleaner and easier selection in **[Loader](artist_tools.md#subset-groups)**

Group name is chosen with use of [profile filtering](#profile-filters)

Applicable context filters:
- **`families`** - Main family of processed subset. `["plate", "model"]`
- **`hosts`** - Host from which publishing was triggered. `["maya", "nuke"]`
- **`tasks`** - Current task. `["modeling", "animation"]`

    ![global_integrate_new_template_name_profile](assets/global_integrate_new_subset_group.png)
    
(This image shows use case where only assets published from 'photoshop', for all families for all tasks should be marked as grouped with a capitalized name of Task where they are published from.)