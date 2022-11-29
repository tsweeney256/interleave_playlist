# Hierarchical Options

These are all of the options supported by scoped hierarchy. They can be used at the
global, location, and group scope.

## `whitelist`

### Description

* Type: List[String]
* Required: False

A case-insensitive list of allowed substrings to be present in filenames. Files are filtered
out before they're considered for interleaving or other options like `timed`.

### Example

Take the following input yml:
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

### Description

* Type: List[String]
* Required: False

A case-insensitive list of dis-allowed substrings to be present in filenames. Files are filtered
out before they're considered for interleaving or other options like `timed`.

### Example

Take the following input yml:

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

### Description

* Type: Integer
* Required: False

A number representing how to order shows in the playlist. Files with lower priority values are
always placed above files with higher priority values. This should be thought in terms of "This is
my #1 priority show", hence priority 1 files will be placed higher in the playlist before priority
2 files.

If two or more groups of files have the same priority level, then those groups will be interleaved
together into a single "priority group". This "priority group" will exist above or below other
"priority groups" depending on their relative priority levels.

### Example

Take the following input yml:

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
🔴 /my/location/foo/foo show - 1.mkv
🔴 /my/location/foo/foo show - 2.mkv
🔵 /my/location/bar/bar show - 1.mkv
🔵 /my/location/bar/bar show - 2.mkv
🟡 /my/location/baz/baz show - 1.mkv
🟡 /my/location/baz/baz show - 2.mkv
🟣 /my/location/fiz/fiz show - 1.mkv
🟣 /my/location/fiz/fiz show - 2.mkv
⭕ /my/location/terible/terrible show - 1.mkv
⭕ /my/location/terible/terrible show - 2.mkv
```

The following playlist order would occur

```
🔵 /my/location/bar/bar show - 1.mkv
🔴 /my/location/foo/foo show - 1.mkv
🔵 /my/location/bar/bar show - 2.mkv
🔴 /my/location/foo/foo show - 2.mkv
🟡 /my/location/baz/baz show - 1.mkv
🟣 /my/location/fiz/fiz show - 1.mkv
🟡 /my/location/baz/baz show - 2.mkv
🟣 /my/location/fiz/fiz show - 2.mkv
⭕ /my/location/terible/terrible show - 1.mkv
⭕ /my/location/terible/terrible show - 2.mkv
```

Notice how "foo" (🔴) and "bar" (🔵) shows are interleaved together, "baz" (🟡) and "fiz" (🟣)
shows are interleaved together, but "foo" (🔴) and "bar" (🔵) shows are not interleaved with
"baz" (🟡) and "fiz" (🟣) shows. The two independently interleaved groups were instead prioritized
based on their priority values, with the "foo"/"bar" (🔴/🔵) group prioritized above the
"baz"/"fiz" (🟡/🟣) group. "terrible" (⭕) show, meanwhile, is at the very bottom and not
interleaved with anything because no other group shares its priority level.

## `timed`

### Description

* Type: Object
* Required: False

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
file ordering.
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

### Example

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

## `weight`

### Description

* Type: String or Integer
* Required: False

Weave groups together by their relative weight instead of interleaving.
This can be used to replace interleaving or can be combined with it by weaving two or more
interleaved groups together by weight.

"Weighted groups" are woven together by their proportional weights until they run out of files
to weave. If a particular weighted group has half of the sum of all weights, then it will be chosen
every other time to have its next file be placed as the next item in the playlist. If it possessed
a third of the total weight, its next file would be placed once every third time as the next
item in the playlist, and so on.

Due to weighted groups being able to 'run out of' files, this will likely result in a "lopsided"
weaving, with the higher weighted files being biased towards the front of the playlist until they
disappear entirely later in the playlist. While this isn't an ideal way to construct playlists more
generally, this is a useful tool if you wanted to, say, focus on a select group of shows while
otherwise keeping the rest of your playlist still reasonably interleaved.

The provided weight can either reference a pre-defined weighted group by name or can
simply create an implicit weighted group by instead providing an integer value for the weight. All
groups within a weighted group will be interleaved, per normal, and will then be woven together
with all other weighted groups, within the same priority group, based on their weight values.
Keep in mind that weighted groups are identified by their name, not by the value of their weight.
Providing an integer will create a unique weighted group that cannot be referenced elsewhere.

All groups will belong to a hidden default group with a weight of `0` if not given one explicitly.
Groups with a weight of `0` are simply placed at the bottom of the priority group below any
weighted groups with non-zero weights. In the event two weighted groups have the same weight,
the tie is broken by the name of the weighted group. The hidden default weighted group will
always be last.


### Example

Take the following input yml:

```yaml
weights:
  - name: foo-weight
    value: 1
locations:
  - name: /my/location/foo
    weight: foo-weight
  - name: /my/location/bar
    weight: 1
```

Also take for example the following file paths:

```
🔴 /my/location/foo/foo show - 1.mkv
🔴 /my/location/foo/foo show - 2.mkv
🔵 /my/location/bar/bar show - 1.mkv
🔵 /my/location/bar/bar show - 2.mkv
🔵 /my/location/bar/bar show - 3.mkv
🔵 /my/location/bar/bar show - 4.mkv
```

The resulting playlist will look like this:

```
🔴 /my/location/foo/foo show - 1.mkv
🔵 /my/location/bar/bar show - 1.mkv
🔴 /my/location/foo/foo show - 2.mkv
🔵 /my/location/bar/bar show - 2.mkv
🔵 /my/location/bar/bar show - 3.mkv
🔵 /my/location/bar/bar show - 4.mkv
```

* Total Weight: 1 + 1 = 2
* `foo-weight` Weight Proportion: 1 / 2 = 0.5
* `/my/location/bar` Weight: 1 / 2 = 0.5

Both groups have a weight proportion of `0.5`, and so both shows will take every other place
in the list. After `foo-weight` runs out of files, the remainder are placed at the bottom of the
list. `foo-weight` came first in this example because it had an explicitly named weighted group
while the other weight group has no name.

**Example #2**

As a more complex example, consider the following input yaml.
```yaml
weights:
  - name: foo-weight
    value: 2
  - name: bar-weight
    value: 1
  - name: baz-weight
    value: 1
locations:
  - name: /my/location/foo
    weight: foo-weight
  - name: /my/location/bar
    regex: (?P<group>.+) - [0-9]+\.mkv
    weight: bar-weight
    groups:
      - name: baz
        weight: baz-weight
```

And consider the following list of file paths:

```
🔴 /my/location/foo/foo show - 1.mkv
🔴 /my/location/foo/foo show - 2.mkv
🔴 /my/location/foo/foo show - 3.mkv
🔴 /my/location/foo/foo show - 4.mkv
🔵 /my/location/bar/bar show - 1.mkv
🔵 /my/location/bar/bar show - 2.mkv
🔵 /my/location/bar/bar show - 3.mkv
🔵 /my/location/bar/bar show - 4.mkv
🟣 /my/location/bar/baz show - 1.mkv
🟣 /my/location/bar/baz show - 2.mkv
🟣 /my/location/bar/baz show - 3.mkv
🟣 /my/location/bar/baz show - 4.mkv
🟡 /my/location/bar/fiz show - 1.mkv
🟡 /my/location/bar/fiz show - 2.mkv
🟡 /my/location/bar/fiz show - 3.mkv
🟡 /my/location/bar/fiz show - 4.mkv
```

The resulting playlist will be:
```
🔴 /my/location/foo/foo show - 1.mkv
🔵 /my/location/bar/bar show - 1.mkv
🔴 /my/location/foo/foo show - 2.mkv
🟣 /my/location/bar/baz show - 1.mkv
🔴 /my/location/foo/foo show - 3.mkv
🟡 /my/location/bar/fiz show - 1.mkv
🔴 /my/location/foo/foo show - 4.mkv
🟣 /my/location/bar/baz show - 2.mkv
🔵 /my/location/bar/bar show - 2.mkv
🟣 /my/location/bar/baz show - 3.mkv
🟡 /my/location/bar/fiz show - 2.mkv
🟣 /my/location/bar/baz show - 4.mkv
🔵 /my/location/bar/bar show - 3.mkv
🟡 /my/location/bar/fiz show - 3.mkv
🔵 /my/location/bar/bar show - 4.mkv
🟡 /my/location/bar/fiz show - 4.mkv
```

**Explanation**

* Total Weight: 2 + 1 + 1 = 4
* `foo-weight` Weight Proportion: 2 / 4 = 0.5
* `bar-weight` Weight Proportion: 1 / 4 = 0.25
* `bar-weight` Weight Proportion: 1 / 4 = 0.25


* "foo show" files are assigned `foo-weight` via location scope.
* "bar show" files are assigned `bar-weight` via location scope.
* "baz show" files are assigned `baz-weight` via group scope.
* "fiz show" files are assigned `bar-weight` via location scope. Only "baz show" has a
group override.


* `bar-weight` groups ("bar show" and "fiz show") are interleaved together.
```
🔵 /my/location/bar/bar show - 1.mkv
🟡 /my/location/bar/fiz show - 1.mkv
🔵 /my/location/bar/bar show - 2.mkv
🟡 /my/location/bar/fiz show - 2.mkv
🔵 /my/location/bar/bar show - 3.mkv
🟡 /my/location/bar/fiz show - 3.mkv
🔵 /my/location/bar/bar show - 4.mkv
🟡 /my/location/bar/fiz show - 4.mkv
```
* `bar-weight` and `baz-weight` groups are weaved together by weight.
    * From the perspective of these two weighted groups, `bar-weight` and `baz-weight`
have a weight proportion of 0.5 each, so each will be woven together every other file
into an intermediate weight group.
    * The two weighted groups, `bar-weight` and `baz-weight`, have the same weigh of `1`,
so the tie is broken by alphabetical ordering, and `bar-weight` comes first.
```
🔵 /my/location/bar/bar show - 1.mkv
🟣 /my/location/bar/baz show - 1.mkv
🟡 /my/location/bar/fiz show - 1.mkv
🟣 /my/location/bar/baz show - 2.mkv
🔵 /my/location/bar/bar show - 2.mkv
🟣 /my/location/bar/baz show - 3.mkv
🟡 /my/location/bar/fiz show - 2.mkv
🟣 /my/location/bar/baz show - 4.mkv
🔵 /my/location/bar/bar show - 3.mkv
🟡 /my/location/bar/fiz show - 3.mkv
🔵 /my/location/bar/bar show - 4.mkv
🟡 /my/location/bar/fiz show - 4.mkv
```
* `foo-weight`, with a weight proportion of 0.5, will be placed every other file into the playlist.
* The intermediate weight group, consisting of `bar-weight` and `baz-weight` weaved together by
weight, has a weight proportion of 0.5 and will be placed every other file into the playlist.
* `foo-weight` will appear first because it was heaviest weight before any
intermediate groups were made.

```
🔴 /my/location/foo/foo show - 1.mkv
🔵 /my/location/bar/bar show - 1.mkv
🔴 /my/location/foo/foo show - 2.mkv
🟣 /my/location/bar/baz show - 1.mkv
🔴 /my/location/foo/foo show - 3.mkv
🟡 /my/location/bar/fiz show - 1.mkv
🔴 /my/location/foo/foo show - 4.mkv
🟣 /my/location/bar/baz show - 2.mkv
🔵 /my/location/bar/bar show - 2.mkv
🟣 /my/location/bar/baz show - 3.mkv
🟡 /my/location/bar/fiz show - 2.mkv
🟣 /my/location/bar/baz show - 4.mkv
🔵 /my/location/bar/bar show - 3.mkv
🟡 /my/location/bar/fiz show - 3.mkv
🔵 /my/location/bar/bar show - 4.mkv
🟡 /my/location/bar/fiz show - 4.mkv
```
