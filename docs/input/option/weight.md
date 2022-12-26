# Weight

## Keywords

* `weights`
    * **Description**: A list of named weight definitions to be used elsewhere.
    * **Scope**: Global
    * **Type**: List[Object]
    * **Required**: False
    * **Default**: `null`
    * **Fields**:
        * `name`
            * **Description**: The name the weight is to be referred by
            * **Type**: String
            * **Required**: True
        * `value`
            * **Description**: The value of the weight
            * **Type**: Integer
            * **Required**: True
* `weight`
    * **Description**: The name of the named weight or the value of an implicit one. Determines
how to weigh the given group.
    * **Scope**: Hierarchical
    * **Type**: String or Integer
    * **Required**: False
    * **Default**: `null`

## Description

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


## Examples

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
🔷 /my/location/bar/bar show - 1.mkv
🔷 /my/location/bar/bar show - 2.mkv
🔷 /my/location/bar/bar show - 3.mkv
🔷 /my/location/bar/bar show - 4.mkv
```

The resulting playlist will look like this:

```
🔴 /my/location/foo/foo show - 1.mkv
🔷 /my/location/bar/bar show - 1.mkv
🔴 /my/location/foo/foo show - 2.mkv
🔷 /my/location/bar/bar show - 2.mkv
🔷 /my/location/bar/bar show - 3.mkv
🔷 /my/location/bar/bar show - 4.mkv
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
🔷 /my/location/bar/bar show - 1.mkv
🔷 /my/location/bar/bar show - 2.mkv
🔷 /my/location/bar/bar show - 3.mkv
🔷 /my/location/bar/bar show - 4.mkv
🟪 /my/location/bar/baz show - 1.mkv
🟪 /my/location/bar/baz show - 2.mkv
🟪 /my/location/bar/baz show - 3.mkv
🟪 /my/location/bar/baz show - 4.mkv
💛 /my/location/bar/fiz show - 1.mkv
💛 /my/location/bar/fiz show - 2.mkv
💛 /my/location/bar/fiz show - 3.mkv
💛 /my/location/bar/fiz show - 4.mkv
```

The resulting playlist will be:
```
🔴 /my/location/foo/foo show - 1.mkv
🔷 /my/location/bar/bar show - 1.mkv
🔴 /my/location/foo/foo show - 2.mkv
🟪 /my/location/bar/baz show - 1.mkv
🔴 /my/location/foo/foo show - 3.mkv
💛 /my/location/bar/fiz show - 1.mkv
🔴 /my/location/foo/foo show - 4.mkv
🟪 /my/location/bar/baz show - 2.mkv
🔷 /my/location/bar/bar show - 2.mkv
🟪 /my/location/bar/baz show - 3.mkv
💛 /my/location/bar/fiz show - 2.mkv
🟪 /my/location/bar/baz show - 4.mkv
🔷 /my/location/bar/bar show - 3.mkv
💛 /my/location/bar/fiz show - 3.mkv
🔷 /my/location/bar/bar show - 4.mkv
💛 /my/location/bar/fiz show - 4.mkv
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
🔷 /my/location/bar/bar show - 1.mkv
💛 /my/location/bar/fiz show - 1.mkv
🔷 /my/location/bar/bar show - 2.mkv
💛 /my/location/bar/fiz show - 2.mkv
🔷 /my/location/bar/bar show - 3.mkv
💛 /my/location/bar/fiz show - 3.mkv
🔷 /my/location/bar/bar show - 4.mkv
💛 /my/location/bar/fiz show - 4.mkv
```
* `bar-weight` and `baz-weight` groups are weaved together by weight.
    * From the perspective of these two weighted groups, `bar-weight` and `baz-weight`
have a weight proportion of 0.5 each, so each will be woven together every other file
into an intermediate weight group.
    * The two weighted groups, `bar-weight` and `baz-weight`, have the same weigh of `1`,
so the tie is broken by alphabetical ordering, and `bar-weight` comes first.
```
🔷 /my/location/bar/bar show - 1.mkv
🟪 /my/location/bar/baz show - 1.mkv
💛 /my/location/bar/fiz show - 1.mkv
🟪 /my/location/bar/baz show - 2.mkv
🔷 /my/location/bar/bar show - 2.mkv
🟪 /my/location/bar/baz show - 3.mkv
💛 /my/location/bar/fiz show - 2.mkv
🟪 /my/location/bar/baz show - 4.mkv
🔷 /my/location/bar/bar show - 3.mkv
💛 /my/location/bar/fiz show - 3.mkv
🔷 /my/location/bar/bar show - 4.mkv
💛 /my/location/bar/fiz show - 4.mkv
```
* `foo-weight`, with a weight proportion of 0.5, will be placed every other file into the playlist.
* The intermediate weight group, consisting of `bar-weight` and `baz-weight` weaved together by
weight, has a weight proportion of 0.5 and will be placed every other file into the playlist.
* `foo-weight` will appear first because it was heaviest weight before any
intermediate groups were made.

```
🔴 /my/location/foo/foo show - 1.mkv
🔷 /my/location/bar/bar show - 1.mkv
🔴 /my/location/foo/foo show - 2.mkv
🟪 /my/location/bar/baz show - 1.mkv
🔴 /my/location/foo/foo show - 3.mkv
💛 /my/location/bar/fiz show - 1.mkv
🔴 /my/location/foo/foo show - 4.mkv
🟪 /my/location/bar/baz show - 2.mkv
🔷 /my/location/bar/bar show - 2.mkv
🟪 /my/location/bar/baz show - 3.mkv
💛 /my/location/bar/fiz show - 2.mkv
🟪 /my/location/bar/baz show - 4.mkv
🔷 /my/location/bar/bar show - 3.mkv
💛 /my/location/bar/fiz show - 3.mkv
🔷 /my/location/bar/bar show - 4.mkv
💛 /my/location/bar/fiz show - 4.mkv
```
