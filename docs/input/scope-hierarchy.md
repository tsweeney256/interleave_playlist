# Scope Hierarchy
## Description
The input yml file is divided into three scopes, ordered most general to most specific:

* Global
* Location
* Group

These scopes are hierarchical and automatically inherit supported settings from
its parent. From this you can override specific settings in a lower scope while
retaining the settings you want more generally defined in a higher scope.

## Supported Settings

The following settings are supported in all three scopes, are inherited by child
scopes, and can be overriden in these child scopes.

* whitelist
* blacklist
* priority
* timed

## Examples

Take the following input file as an example:

```yaml
whitelist:
  - '.mkv'
  - '.mp4'
locations:
  - name: '/my/location/foo'
    regex: '(?P<group>.+) - [0-9]+.+'
    whitelist:
      - 'mkv'
    groups:
      - name: 'old show'
        whitelist:
          - 'avi'
  - name: '/my/location/bar'
    regex: '(?P<group>.+) - [0-9]+.+'
    groups:
      - name: 'cool show'
  - name: '/my/location/baz'
    whitelist:
      - ''
```

* At the global scope, only `.mkv` and `.mp4` files are whitelisted.
* In `/my/location/foo`, only `.mkv` files are whitelisted.
* Files that match the group expression, `old show` in that location,
only have `.avi` files whitelisted.
* Meanwhile, in `/my/location/bar`, the global whitelist of `.mkv` and `.mp4` are inherited.
* Additionally, files that match the group expression `cool show` in that location
also inherit the global whitelist of `.mkv` and `.mp4`.

Assuming we had the following files, this is how they would get filtered based
on these scoping rules.

* ✅ **/my/location/foo/fun show - 01.mkv**
    * `.mkv` is allowed for location override
* ❌ **/my/location/foo/neat show - 01.mp4**
    * global whitelist was overriden, so `.mp4` is not whitelisted in this location
* ✅ **/my/location/foo/old show - 01.avi**
    * `.avi` is allowed for this group override
* ❌ **/my/location/foo/old show - 02.mkv**
    * location whitelist was overriden so `.mkv` is not whitelisted in this group
* ✅ **/my/location/bar/awesome show - 01.mkv**
    *  `mkv` is allowed due to inheriting from global scope
* ✅ **/my/location/bar/lousy show - 01.mp4**
    *  `mp4` is allowed due to inheriting from global scope
* ❌ **/my/location/bar/ancient show - 01.wmv**
    * `wmv` is not allowed due to not being present from inherited global scope
* ✅ **/my/location/bar/cool show - 01.mp4**
    * `mp4` is allowed due to inheriting from location scope,
which further inherited from global scope
* ✅ **/my/location/baz/alright movie.mov**
    *  whitelist overridden in location scope to be disabled, so all files in location are allowed
