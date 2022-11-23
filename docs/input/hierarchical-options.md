# Hierarchical Options

These are all of the options supported by scoped hierarchy. They can be used at the
global, location, and group scope.

## `whitelist`
* Type: list[string]
* Required: false

A case-insensitive list of allowed substrings to be present in filenames. Files are filtered
out before they're considered for interleaving or other options like `timed`.

For example, take the following input yml:
```yaml
whitelist:
  - mp4
  - mkv
locations:
  - name: /my/location/foo/
  - name: /my/location/bar/mp4/
```

Given the following file paths, this is what will be placed in the playlist:

* ✅ **/my/location/foo/show.MKV**
    * `mkv` is a case-insensitive subset of `show.MKV`
* ✅ **/my/location/foo/show.mp4**
    * `mp4` is a case-insensitive subset of `show.mp4`
* ❌ **/my/location/foo/show.avi**
    * nothing in the whitelist is a subset of `show.avi`
* ❌ **/my/location/bar/mp4/show.avi**
    * nothing in the whitelist is a subset of `show.avi`, even if the full path contains `mp4`

## `blacklist`
* Type: list[string]
* Required: false

A case-insensitive list of dis-allowed substrings to be present in filenames. Files are filtered
out before they're considered for interleaving or other options like `timed`.

For example, take the following input yml:
```yaml
blacklist:
  - 720p
  - 1280x720
locations:
  - name: /my/location/foo/
  - name: /my/location/bar/720p/
```
Given the following file paths, this is what will be placed in the playlist:

* ❌ **/my/location/foo/show (720P).mkv**
    * `720p` is a case-insensitive subset of `show (720P).mkv`
* ❌ **/my/location/foo/show (1280x720).mkv**
    * `1280x720` is a case-insensitive subset of `show (1280x720).mkv`
* ✅ **/my/location/foo/show.avi**
    * nothing in the blacklist is a subset of `show.avi`
* ✅ **/my/location/bar/720p/show.avi**
    * nothing in the blacklist is a subset of `show.avi`, even if the full path contains `720p`

## `priority`
* Type: integer
* Required: false

A number representing how to order shows in the playlist. Files with lower priority values are
always placed above files with higher priority values. This should be thought in terms of "This is
my #1 priority show", hence priority 1 files will be placed higher in the playlist before priority
2 files.

If two or more groups of files have the same priority level, then those groups will be interleaved
together into a single "priority group". This "priority group" will exist above or below other
"priority groups" depending on their relative priority levels.

As an example, take the following input yml:

```yaml
locations:
  - name: /my/location/foo
    priority: 1
  - name: /my/location/bar
    priority: 1
  - name: /my/location/baz
    priority: 2
  - name: /my/location/fiz
    priority: 2
  - name: /my/location/terrible
    priority: 999
```

Given the following list of file paths:
```
/my/location/foo/foo show - 1.mkv
/my/location/foo/foo show - 2.mkv
/my/location/bar/bar show - 1.mkv
/my/location/bar/bar show - 2.mkv
/my/location/baz/baz show - 1.mkv
/my/location/baz/baz show - 2.mkv
/my/location/fiz/fiz show - 1.mkv
/my/location/fiz/fiz show - 2.mkv
/my/location/terible/terrible show - 1.mkv
/my/location/terible/terrible show - 2.mkv
```

The following playlist order would occur

```
/my/location/bar/bar show - 1.mkv
/my/location/foo/foo show - 1.mkv
/my/location/bar/bar show - 2.mkv
/my/location/foo/foo show - 2.mkv
/my/location/baz/baz show - 1.mkv
/my/location/fiz/fiz show - 1.mkv
/my/location/baz/baz show - 2.mkv
/my/location/fiz/fiz show - 2.mkv
/my/location/terible/terrible show - 1.mkv
/my/location/terible/terrible show - 2.mkv
```

Notice how "foo" and "bar" shows are interleaved together, "baz" and "fiz" shows are interleaved
together, but "foo" and "bar" shows are not interleaved with "baz" and "fiz" shows. The two
independently interleaved groups were instead prioritized based on their priority values, with
the "foo"/"bar" group prioritized above the "baz"/"fiz" group. "terrible" show, meanwhile,
is at the very bottom not interleaved with anything because no other group shares its priority
level.

## `timed`

* Type: object
* Required: false

Allows you to control when files appear in the playlist based on cron rules you define. This is
useful if you want to do something like watch a show weekly with a friend, or if you want to
schedule when you watch what shows.

`timed` takes the following options:

* `start`
    * required
    * ISO date string in the form of `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`
        * This datetime will be relative to the user's current timezone. You can set an explicit
timezone, if desired, by appending a timezone in the form of `+HH:MM:SS`, such as `-04:00:00`
for EDT.
        * When using explicitly defined timezones, automatic daylight savings time adjustments
are not supported. Daylight savings time works correcly when using the default timezone from
your operating system. Support for explicit IANA timezones, which consider daylight savings,
may be added in the future.
        * Technically supports any format [listed here](https://docs.python.org/3.9/library/datetime.html#datetime.datetime.fromisoformat)
    * This represents when the `timed` rule will take effect. This does *not* represent when
you'll start seeing files appear in the playlist, necessarily. For a file to appear in the
playlist, both the start datetime must have passed *and* the cron rule must have been
activated at least once since then. If both `start` and `cron` are true at the same moment, then
the set `amount` of episodes will be placed into the playlist, regardless of the value of
`start-at-cron`.
* `cron`
    * required
    * [cron expression](https://en.wikipedia.org/wiki/Cron#Cron_expression)
        * e.g. `0 3 * * TUE`, every Tuesday at 3AM
    * This represents how often you want new files to appear in the playlist once the
start date has passed.
* `first`
    * default: `1`
    * integer
    * This represents the first file that should be placed in the playlist. All future
files will be placed starting after this one. This is useful if you wanted to start at, say,
the 7th episode of a show you already started watching. Which file is considered to be file
`1`, `2`, `3`, etc. is based entirely on the alphabetical ordering of the filenames. Files
filtered out due to rules such as `whitelist` and `blacklist` occur before determining the
file ordering.
* `amount`
    * default: `1`
    * integer
    * This represents how many files should be placed in the playlist once the cron duration
has elapsed. This is useful if you like watching more than one episode at a time.
* `start-at-cron`
    * default: `true`
    * boolean
    * Normally files don't get added by the `timed` feature until both the start date has been
reached *and* a valid datetime has occurred past the start date that matches the cron
expression. Setting this to `false` will make it so merely reaching the start date results
in the first file(s) entering the playlist. Once the cron elapses after the start date,
even if it's only a second later, the second batch of file(s) will enter the playlist.
If `start` and `cron` resolve at the exact same moment, this option has no effect and the
first file(s) will enter the playlist when `start` and `cron` occurs.

**Example #1**

As an example, take the following input yml:

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
