# Timed

## Keywords

* `timed`
    * **Description**: Schedules when files should be placed in the playlist
    * **Scope**: Hierarchical
    * **Type**: Object
    * **Required**: False
    * **Default**: `null`
    * **Fields**:
        * `start`
            * **Description**: What datetime this rule should take effect. Still must meet cron
expression before the file is added to the playlist if `start-at-cron` is `false`
            * **Type**: String
                * In the form of `YYYY-MM-DD`
            * **Required**: True
        * `cron`
            * **Description**: Cron Expression
            * **Type**: String
                * E.g.  `0 3 * * TUE`, every Tuesday at 3AM
            * **Required**: True
        * `first`
            * **Description**: Which index file the rule should start with. 1-indexed.
            * **Type**: Integer
            * **Required**: False
            * **Default**: 1
        * `amount`
            * **Description**: How many files should be placed in the playlist per cron period
            * **Type**: Integer
            * **Required**: False
            * **Default**: 1
        * `start-at-cron`
            * **Description**: Determines if the first batch of files needs to wait for the first
cron period before entering the playlist.
            * **Type**: boolean
            * **Required**: False
            * **Default**: True

## Description

Allows you to control when files appear in the playlist based on cron rules you define. This is
useful if you want to do something like watch a show weekly with a friend, or if you want to
schedule when you watch what shows.

`timed` takes the following options:

* `start`
    * Type: ISO Date String
    * Required: True
        * In the form of `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`
            * Technically supports any format [listed here](https://docs.python.org/3.9/library/datetime.html#datetime.datetime.fromisoformat)
        * This datetime will be relative to the user's current timezone. You can set an explicit
timezone offset, if desired, by appending a timezone in the form of `+HH:MM:SS`, such as `-04:00:00`
for EDT.
        * When using explicitly defined timezone offsets, automatic daylight savings time
adjustments are not supported. Daylight savings time works correcly when using the default
timezone from your operating system. Support for explicit IANA timezones, which consider daylight
savings, may be added in the future.
    * This represents when the `timed` rule will take effect. This does *not* represent when
you'll start seeing files appear in the playlist, necessarily. For a file to appear in the
playlist, both the start datetime must have passed *and* the cron rule must have been
activated at least once since then. If both `start` and `cron` are true at the same moment, then
the set `amount` of episodes will be placed into the playlist, regardless of the value of
`start-at-cron`.
* `cron`
    * Type: [Cron Expression String](https://en.wikipedia.org/wiki/Cron#Cron_expression)
        * e.g. `0 3 * * TUE`, every Tuesday at 3AM
    * Required: True
    * This represents how often you want new files to appear in the playlist once the
start date has passed.
* `first`
    * Type: Integer
    * Required: False
    * Default: `1`
    * This represents the first file that should be placed in the playlist. All future
files will be placed starting after this one. This is useful if you wanted to start at, say,
the 7th episode of a show you already started watching. Which file is considered to be file
`1`, `2`, `3`, etc. is based entirely on the alphabetical ordering of the filenames. Files
filtered out due to rules such as `whitelist` and `blacklist` occur before determining the
file ordering. 1-indexed.
* `amount`
    * Type: Integer
    * Required: False
    * Default: `1`
    * This represents how many files should be placed in the playlist once the cron duration
has elapsed. This is useful if you like watching more than one episode at a time.
* `start-at-cron`
    * Type: Boolean
    * Required: False
    * Default: `true`
    * Normally files don't get added by the `timed` feature until both the start date has been
reached *and* a valid datetime has occurred past the start date that matches the cron
expression. Setting this to `false` will make it so merely reaching the start date results
in the first file(s) entering the playlist. Once the cron elapses after the start date,
even if it's only a second later, the second batch of file(s) will enter the playlist.
If `start` and `cron` resolve at the exact same moment, this option has no effect and the
first file(s) will enter the playlist when `start` and `cron` occurs.

## Examples

**Example #1**

Take the following input yml:

```yaml
locations:
  - name: /my/location/foo
    timed:
      start: '2022-11-21' # Monday
      cron: '0 3 * * TUE'
      first: 2
      amount: 2
      start-at-cron: true
```

Additionally assume the following file paths:
```
/my/location/foo/foo show - 1.mkv
/my/location/foo/foo show - 2.mkv
/my/location/foo/foo show - 3.mkv
/my/location/foo/foo show - 4.mkv
/my/location/foo/foo show - 5.mkv
```

The playlist on Monday 2022-11-21 will be empty. While the start date has been reached,
the cron expression, which runs every Tuesday at 3AM, has yet to happen.

On Tuesday 2022-11-22 3AM, the playlist will look like the following:
```
/my/location/bar/bar show - 2.mkv
/my/location/bar/bar show - 3.mkv
```

The rule was set to start at the second file, and to add two files at once to the playlist.

On 2022-11-29 3AM, the playlist will look like the following:
```
/my/location/foo/foo show - 2.mkv
/my/location/foo/foo show - 3.mkv
/my/location/foo/foo show - 4.mkv
/my/location/foo/foo show - 5.mkv
```

A week has passed and the last two episodes are added to the playlist. Past this point the
`timed` rule won't do anything further.

**Example #2**

As a second example, take the following input yml:
```yaml
locations:
  - name: /my/location/bar
    timed:
      start: '2022-11-21'
      cron: '0 3 * * TUE'
      first: 1
      amount: 1
      start-at-cron: false
```

Additionally assume the following file paths:
```
/my/location/bar/bar show - 1.mkv
/my/location/bar/bar show - 2.mkv
/my/location/bar/bar show - 3.mkv
/my/location/bar/bar show - 4.mkv
/my/location/bar/bar show - 5.mkv
```

Notice that this time `start-at-cron` is false, and this time we're starting at the first file
and only doing one file at a time.

The playlist on Monday 2022-11-21 will look like the following:
```
/my/location/bar/bar show - 1.mkv
```

The cron expression has yet to be met, but `start-at-cron` is set to `false`, so the first
file was added to the playlist anyway.

The playlist on Tuesday 2022-11-22 3AM will look like the following:
```
/my/location/bar/bar show - 1.mkv
/my/location/bar/bar show - 2.mkv
```

Even though the cron is set to run weekly, only one day has passed and a file was added to the
playlist. From here the episodes will simply be added to the playlist on a weekly basis like the
last example, just one at a time this time.
