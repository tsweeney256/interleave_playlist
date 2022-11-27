# Interleave Playlist Todo

## Parking Lot

* TOML (maybe)
  * Use [this mkdocs plugin](https://github.com/yacir/markdown-fenced-code-tabs) for docs
* mpv IPC integration (maybe)

## Alpha 8

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
  * [ ] `default` regex
* [ ] Run simulation tests with `weighted`



## Alpha 9

- [ ] Rewrite loading bar
- [ ] Full interface test coverage
- [ ] `(?P<pretty>)` feature
- [ ] timed IANA support
- [ ] group amounts. when  group is interleaved, do so as a batch of X episodes at once
- [ ] cache file durations
- [ ] Update PySide for python 3.11 support
- [ ] Fix PyPi being called "Interleave-Playlist"
- [ ] reminder popup to mark things watched if left app open at least equal or greater duration than first file
duration time



## Alpha 10

- [ ] Update notification with release notes
- [ ] About box
- [ ] License box
- [ ] Ignore update option
  - [ ] store in state file
  - [ ] button on update popup
  - [ ] ignore all updates option



## Alpha 11

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



## Alpha 12

- [ ] GUI for settings file
- [ ] Pause `timed` feature
  * timed pause table containing hierarchy name, start date, end date
  * sum all start/end intervals and subtract from normal "current" ep for a given hierarchy name.



## Alpha 13

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
