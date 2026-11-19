# Test results (auto-generated)

## How these numbers were made
- 10 test prompts in 5 groups, written in MS-COCO caption style.
- For each prompt the model generated **4 images** (DDIM, **20 steps**, guidance scale **5.0**, fixed seed per prompt).
- Every image was scored by CLIP (ViT-B/32): a 0-100 similarity between the image and its prompt. Higher means a closer match.
- Per prompt, the images were ranked; the **best**, a **typical** (median) and the **worst** were kept.
- Prompts were then ranked against each other by their best score, and each group was averaged.
- **Caveat:** CLIP is an automatic, imperfect judge and these are small samples. Check the figures by eye; scores alone prove little.

## Group summary

| Group | Prompts | Avg best | Avg mean | Avg worst |
|---|---|---|---|---|
| 1_rigid_scenes | 2 | 30.3 | 28.8 | 27.3 |
| 2_animals | 2 | 33.3 | 31.4 | 28.6 |
| 3_people_sports | 2 | 30.1 | 27.8 | 24.9 |
| 4_outdoor_scenes | 2 | 26.1 | 24.3 | 22.1 |
| 5_out_of_domain | 2 | 26.3 | 24.7 | 22.2 |

## What each group is meant to show

- **1_rigid_scenes**: Common objects with fairly fixed shapes. Expected to be the model's strongest group.
- **2_animals**: Animals change pose a lot. Expect correct colour, texture and setting but weak body structure.
- **3_people_sports**: People are the hardest subject for a small model. Expect distorted anatomy.
- **4_outdoor_scenes**: Landscapes have little fine structure, so they are usually forgiving.
- **5_out_of_domain**: Things COCO never contained (fantasy, text, exact counts). These are deliberate failure cases.

## Plain observations from the numbers

- Highest average CLIP score: **2_animals** (31.4). Lowest: **4_outdoor_scenes** (24.3).
- Best single result: "a herd of sheep grazing on a hill" (34.0). Lowest-ranked prompt: "a snowy mountain with trees" (24.7).
- Average gap between the best and worst image of the same prompt: 4.2 CLIP points, which is why best-of-4 selection helps.
- Confirm these against the figures before writing them in the report.

## Ranked prompts

| # | Group | Prompt | Best | Typical | Worst |
|---|---|---|---|---|---|
| 1 | 2_animals | a herd of sheep grazing on a hill | 34.0 | 31.2 | 27.3 |
| 2 | 2_animals | a giraffe standing in a grassy field | 32.6 | 30.6 | 29.8 |
| 3 | 3_people_sports | a man riding a wave on a surfboard | 31.0 | 29.2 | 27.8 |
| 4 | 1_rigid_scenes | a red bus driving down a city street | 30.8 | 29.8 | 29.2 |
| 5 | 1_rigid_scenes | a train traveling down the tracks | 29.8 | 26.5 | 25.3 |
| 6 | 3_people_sports | a man riding a skateboard down a street | 29.2 | 25.6 | 22.1 |
| 7 | 4_outdoor_scenes | a boat floating on a calm lake | 27.6 | 23.4 | 20.1 |
| 8 | 5_out_of_domain | a futuristic city with flying cars | 27.0 | 25.1 | 23.7 |
| 9 | 5_out_of_domain | a dragon flying over a castle | 25.5 | 23.7 | 20.8 |
| 10 | 4_outdoor_scenes | a snowy mountain with trees | 24.7 | 24.4 | 24.1 |

## Files
- `fig_<group>_N.png`: best / typical / worst per prompt
- `fig_ranking_all.png`: every prompt's best image, ranked
- `results_ranked.csv`, `group_summary.csv`: tables
- `images/`: every saved image (`*_best512.png` is the best, enlarged to 512 px)