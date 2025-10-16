# Profilarr Database
This is a [Profilarr Compliant Database](https://dictionarry.dev/profilarr-setup/linking?section=database-spotlight) that can be used with [Profilarr](https://dictionarry.dev) to sync quality profiles between Radarr and Sonarr. The goal of this project is to have a consistently updated database of quality profiles based on the changes in either Dictionarry or TRaSH Guides.

The profiles implemented so far include the ones in the original [Dictionarry database](https://github.com/Dictionarry-Hub/database), and all the profiles from [TRaSH Guides](https://trash-guides.info), including French, German, SQP and Anime classifications. 
*Note: All custom formats defined by TRaSH (including those not in any quality profile) have been included in this database, for users to use and customise as they wish.*

Special thanks to all those involved in the above projects for making their data available to work with. Additional thanks to [sweatyeggs69's database project](https://github.com/sweatyeggs69/profilarr) which provided a secondary foundation to my understanding of how Profilarr works.

## Usage
### Requirements
Working instances of:
- Profilarr
- Radarr and/or Sonarr

### Linking to Profilarr
Since Profilarr only allows linking to one database at a time, the base quality profiles found in Dictionarry have been kept (and are automatically updated). Use the [official guide](https://dictionarry.dev/profilarr-setup/linking) to link your Profilarr instance to this database.

Some points to note:
- You might need to change any existing *arr app connections to "Manual" instead of "On Pull" or "Scheduled".
- Any existing quality profiles and custom formats will not be removed.

## Development
### General Guidelines
- All changes are to be made strictly in the `scripts` folder, but the full repository should be cloned for ideal development work.
- Local changes to quality profiles, custom formats, and/or regex patterns should **NOT** be pushed to the repository.
- Typically there is no need to manually edit/push the `scripts/trash-cf-maapping.json` file.
### Local Testing
- Once this repository has been cloned, you can also clone the [TRaSH Guides repository](https://github.com/TRaSH-Guides/Guides) for local testing.
- Run each of the following commands for a full demonstration of the parsed profiles.
  ```
  python scripts/trash_custom_format_id_mapper.py <TRaSH Guide repository directory>
  python scripts/trash_custom_format_parser.py <TRaSH Guide repository directory>
  python scripts/trash_profile_parser.py <TRaSH Guide repository directory>
  ```

## Suggestions/Requests
- Since this project was mainly fueled by my desire to have an automated quality profile system, I have set it up to be mostly to my tastes. If you have a special tweak that you apply for your needs, I may be able to incorporate that in as another profile, as long as it can be put into script form.
- I know that a lot of optimisations can be done, so I'm open to any ideas and ways of improvement.
- 
- 
