# Interleave Playlist Todo

## Parking Lot

* TOML (maybe)
  * Use [this mkdocs plugin](https://github.com/yacir/markdown-fenced-code-tabs) for docs
* mpv IPC integration (maybe)
* Context menu
  * Do standard actions
  * See stats like priority/weight/group
  * Change priority
  * Change weight
  * Make app startup not rely on creating a playlist first
* non-FS based locations
  * text file
* priority names (like weight and regex names)

## Alpha 10

* [ ] Validation for:
  * [ ] input file
  * [ ] watched file
  * [x] settings file
  * [ ] state file
* [ ] Weighted
  * [x] core
  * [x] playlist
  * [ ] input
  * [ ] memory? (figure something out for this)
* [ ] Full persistence code coverage
  * [ ] input
  * [ ] watched
  * [x] settings
  * [x] state
* [ ] `start-at-cron` should default to `true`
* [ ] Documentation
* [ ] Last version used in state file, warning when downgraded
* [ ] Regex refactor
  * [ ] define regexes globally and reference in locations
  * [ ] `default` regex defined in settings.yml
  * [ ] allow regex at global scope
* [ ] Run simulation tests with `weighted`
* [ ] Theme horizontal scrollbar too
* [ ] Test all documentation examples
* [ ] Priority groups should be "stable" if no new additions or subtractions

## Alpha 11

- [ ] Rewrite loading bar
- [ ] Full interface test coverage
- [ ] `(?P<pretty>)` feature
- [ ] `(?P<sort>)` regex group
- [ ] timed IANA support
- [ ] group amounts. when  group is interleaved, do so as a batch of X episodes at once
- [ ] cache file durations
- [ ] Update PySide for python 3.11 support
- [ ] Fix PyPi being called "Interleave-Playlist"
- [ ] reminder popup to mark things watched if left app open at least equal or greater duration than first file
duration time

## Alpha 12

- [ ] Update notification with release notes
- [ ] About box
- [ ] License box
- [ ] Ignore update option
  - [ ] store in state file
  - [ ] button on update popup
  - [ ] ignore all updates option

## Alpha 13

- [ ] Actual GUI for watched file
- [ ] Convert watched file to DB
- [ ] Move dropped shows to DB
- [ ] Record more statistics in DB
  - [ ] datetime when episode watched
  - [ ] datetime when show dropped,
  - [ ] (maybe) datetime when episode first enters playlist
- [ ] location names refactor
  - [ ] treat `name` purely as id
  - [ ] remove `additional`
  - [ ] add new `paths` field for list of paths
  - [ ] Wizard to update incompatibilities in input yaml and db
- [ ] Allow identifying groups by regex rather than just substring
- [ ] Consider removing restriction on requiring named capture `group`

## Alpha 14

- [ ] GUI for settings file
- [ ] Pause `timed` feature
  * timed pause table containing hierarchy name, start date, end date
  * sum all start/end intervals and subtract from normal "current" ep for a given hierarchy name.

## Alpha 15

- [ ] "Where's my file?" GUI

## RC 1

- [ ] GUI for input file

## 1.0.0

- [ ] No discernible bugs

- [ ] Windows executable
  - [ ] Package `mediainfo`

## 1.1.0

- [ ] CLI
  - [ ] `--play`
  - [ ] `--input`
  - [ ] `--settings`
  - [ ] `--sort`
  - [ ] `--reverse`
  - [ ] `--filter`
  - [ ] Per setting flag
- [ ] Run arbitrary commands on events such as being marked watched or dropped
